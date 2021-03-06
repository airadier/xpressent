/*
Copyright 2009, Alvaro J. Iradier
This file is part of xPressent (Windows Mobile Remote).

xPressent is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

xPressent is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with xPressent.  If not, see <http://www.gnu.org/licenses/>.
*/

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
		public delegate void CurrentSlideReceivedDelegate(int pageNum, Bitmap img, string notes);
		public delegate void NextSlideReceivedDelegate(int pageNum, Bitmap img);
		public delegate void PrevSlideReceivedDelegate(int pageNum, Bitmap img);

		public event ErrorRaisedDelegate ErrorRaised;
		public event CurrentSlideReceivedDelegate CurrentSlideReceived;
		public event NextSlideReceivedDelegate NextSlideReceived;
		public event PrevSlideReceivedDelegate PrevSlideReceived;

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

				try
				{				
					this.sock.Close();
					this.sock = null;
				}
				catch { }

				this.protocolThread.Abort();
				this.protocolThread = null;


			}			
		}

		public void NextSlide()
		{
			this.SendKey(280);
		}

		public void PrevSlide()
		{
			this.SendKey(281);
		}


		public void SendKey(int keyNum)
		{
			this.sendInt(PacketKeyPress);
			this.sendInt(4);
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
			this.sendInt(8);
			this.sendInt(this.width);
			this.sendInt(this.height);

			int version = receiveInt();
			if (version > ProtocolVersion)
			{
				raiseError("Unsupported server version: " + version);
				this.sock.Close();
				return;
			}

			if (receiveInt() != PacketHello || receiveInt() != 0)
			{
				raiseError("Unexpected packet received");
				this.sock.Close();
				return;
			}

			int pageNum;
			System.IO.MemoryStream stream;

			while (!finishThread)
			{
				try
				{
					int packetType = this.receiveInt();
					int packetLen = this.receiveInt();
					switch (packetType)
					{

						case PacketCurrentSlide:
							pageNum = this.receiveInt();
							int jpegSize = this.receiveInt();
							stream = new System.IO.MemoryStream(this.receiveBytes(jpegSize));
							int notesSize = this.receiveInt();
							byte[] notesData = this.receiveBytes(notesSize);

							if (this.CurrentSlideReceived != null)
								this.CurrentSlideReceived(pageNum,
									new Bitmap(stream),
									Encoding.UTF8.GetString(notesData, 0, notesData.Length).Replace("\n", "\r\n"));

							stream.Close();
							
							break;

						case PacketNextSlide:
							pageNum = this.receiveInt();
							stream = new System.IO.MemoryStream(receiveBytes(packetLen - 4));
							nextSlideReceived(pageNum, new Bitmap(stream));
							stream.Close();
							break;

						case PacketPrevSlide:
							pageNum = this.receiveInt();
							stream = new System.IO.MemoryStream(receiveBytes(packetLen - 4));
							prevSlideReceived(pageNum, new Bitmap(stream));
							stream.Close();
							break;

						default:
							this.receiveBytes(packetLen);
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


		protected void raiseError(string msg)
		{
			if (this.ErrorRaised != null)
				this.ErrorRaised(msg);
		}


	}
}
