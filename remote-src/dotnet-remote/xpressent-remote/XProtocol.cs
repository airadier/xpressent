using System;
using System.Collections.Generic;
using System.Text;
using Microsoft.WindowsMobile.SharedSource.Bluetooth;
using System.Net;
using System.Drawing;
using System.Threading;
using System.Net.Sockets;


namespace xpressent_remote
{
	public class XProtocol
	{
		/* xPressent Service UUID */
		const string ServiceUUID = "829abc54-a67d-0e10-ba67-00bc59a5ce41";
		const int ProtocolVersion = 1;
		const int PacketHello = 0;
		const int PacketKeyPress = 1;
		const int PacketCurrentSlide = 2;
		const int PacketNextSlide = 3;
		const int PacketPrevSlide = 4;
		const int PacketNotes = 5;

		public delegate void ErrorRaisedDelegate(string errorMsg);
		public delegate void CurrentSlideReceivedDelegate(int pageNum, Bitmap img);
		public delegate void NextSlideReceivedDelegate(int pageNum, Bitmap img);
		public delegate void PrevSlideReceivedDelegate(int pageNum, Bitmap img);
		public delegate void NotesReceivedDelegate(string notes);

		public event ErrorRaisedDelegate ErrorRaised;
		public event CurrentSlideReceivedDelegate CurrentSlideReceived;
		public event NextSlideReceivedDelegate NextSlideReceived;
		public event PrevSlideReceivedDelegate PrevSlideReceived;
		public event NotesReceivedDelegate NotesReceived;

		/* Boolean to tell the communication thread to exit */
		bool finishThread = false;
		BluetoothDevice btDev = null;
		NetworkStream sock = null;
		Thread protocolThread;
		int width, height;

		public XProtocol(BluetoothDevice btDev, int clientWidth, int clientHeight)
		{
			this.btDev = btDev;
			this.width = clientWidth;
			this.height = clientHeight;
		}

		public void Connect()
		{
			if (this.protocolThread != null)
			{
				Disconnect();
			}
			this.startProtocol();
		}

		public void Disconnect()
		{
			if (this.protocolThread != null)
			{
				this.finishThread = true;
				this.protocolThread.Join(500);
				this.protocolThread.Abort();
				this.protocolThread = null;

				try
				{
					this.sock.Close();
				}
				catch { }

			}			
		}

		public void SendKey(int keyNum)
		{
			this.sendInt(PacketKeyPress);
			this.sendInt(keyNum);
		}

		protected void startProtocol()
		{
			if (this.btDev == null) return;

			this.protocolThread = new Thread(this.runProtocol);
			this.protocolThread.Start();
		}

		protected void runProtocol()
		{
			try
			{
				this.sock = this.btDev.Connect(new System.Guid(ServiceUUID));
			}
			catch (SocketException)
			{
				raiseError("Couldn't connect to target device");
				return;
			}
			catch (Exception)
			{
				raiseError("General error trying to conncet to target device");
				return;
			}

			this.sendInt(ProtocolVersion);
			this.sendInt(PacketHello);
			this.sendInt(this.width);
			this.sendInt(this.height);

			int version = receiveInt();
			if (version > ProtocolVersion)
			{
				raiseError("Unsupported server version: " + version);
				this.sock.Close();
				return;
			}

			if (receiveInt() != PacketHello)
			{
				raiseError("Unexpected packet received");
				this.sock.Close();
				return;
			}

			int size;
			int pageNum;
			System.IO.MemoryStream stream;

			while (!finishThread)
			{
				try
				{
					int type = this.receiveInt();
					switch (type)
					{

						case PacketCurrentSlide:
							size = this.receiveInt();
							pageNum = this.receiveInt();
							stream = new System.IO.MemoryStream(receiveBytes(size));
							currentSlideReceived(pageNum, new Bitmap(stream));
							stream.Close();
							break;

						case PacketNextSlide:
							size = this.receiveInt();
							pageNum = this.receiveInt();
							stream = new System.IO.MemoryStream(receiveBytes(size));
							nextSlideReceived(pageNum, new Bitmap(stream));
							stream.Close();
							break;

						case PacketPrevSlide:
							size = this.receiveInt();
							pageNum = this.receiveInt();
							stream = new System.IO.MemoryStream(receiveBytes(size));
							prevSlideReceived(pageNum, new Bitmap(stream));
							stream.Close();
							break;

						case PacketNotes:
							size = this.receiveInt();
							byte[] notesData = receiveBytes(size);
							notesReceived(Encoding.UTF8.GetString(notesData, 0, notesData.Length).Replace("\n","\r\n"));
							//MessageBox.Show("Notes:" + Encoding.UTF8.GetString(notesData, 0, notesData.Length));
							break;

						default:
							raiseError("Unknown packet type" + type );
							break;
					}
				}
				catch (Exception ex)
				{
					if (!this.finishThread)
					{
						raiseError(ex.Message);
					}
					break;
				}
			}

			try
			{
				this.sock.Close();
			}
			catch { }
			this.sock = null;

		}

		protected byte[] receiveBytes(int amount)
		{
			int read = 0;
			byte[] data = new byte[amount];
			while (read < amount)
			{
				read += this.sock.Read(data, read, amount - read);
				if (read <= 0)
				{
					throw new Exception("Read error");
				}
			}
			return data;
		}

		protected int receiveInt()
		{
			int read = 0;
			byte[] data = new byte[4];
			while (read < 4)
			{
				read += this.sock.Read(data, read, 4 - read);
				if (read <= 0)
				{
					throw new Exception("Read error");
				}
			}
			return IPAddress.NetworkToHostOrder(BitConverter.ToInt32(data, 0));
		}

		protected void sendInt(int value)
		{
			if (this.sock == null || !this.sock.CanWrite) return;
			byte[] data = BitConverter.GetBytes(
				IPAddress.HostToNetworkOrder(value)
			);
			this.sock.Write(data, 0, data.Length);
		}

		protected void currentSlideReceived(int pageNum, Bitmap img)
		{
			if (this.CurrentSlideReceived != null)
				this.CurrentSlideReceived(pageNum, img);
		}

		protected void nextSlideReceived(int pageNum, Bitmap img)
		{
			if (this.NextSlideReceived != null)
				this.NextSlideReceived(pageNum, img);
		}

		protected void prevSlideReceived(int pageNum, Bitmap img)
		{
			if (this.PrevSlideReceived != null)
				this.PrevSlideReceived(pageNum, img);
		}

		protected void notesReceived(string notes)
		{
			if (this.NotesReceived != null)
				this.NotesReceived(notes);
		}

		protected void raiseError(string msg)
		{
			if (this.ErrorRaised != null)
				this.ErrorRaised(msg);
		}


	}
}
