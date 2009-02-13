using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using Microsoft.WindowsMobile.SharedSource.Bluetooth;

namespace xpressent_remote
{
	public partial class MainForm : Form
	{
		const string ServiceUUID = "829abc54-a67d-0e10-ba67-00bc59a5ce41";
		const int ProtocolVersion = 1;
		const int PacketHello = 0;
		const int PacketKeyPress = 1;
		const int PacketCurrentSlide = 2;
		const int PacketNextSlide = 3;
		const int PacketPrevSlide = 4;
		const int PacketNotes = 5;

		bool finishThread = false;
		BluetoothDevice btDev = null;
		NetworkStream sock = null;
		Thread protocolThread;
		Image currentSlide;
		string currentNotes;

		public MainForm()
		{
			InitializeComponent();
		}

		private void MainForm_Load(object sender, EventArgs e)
		{
			btDev = SelectDevice.Run();
			if (btDev == null)
			{
				this.Close();
				return;
			}

			try
			{
				sock = btDev.Connect(new System.Guid(ServiceUUID));
			}
			catch (SocketException)
			{
				showError("Couldn't connect to target device");
				this.Close();
				return;
			}
			catch (Exception)
			{
				showError("General error trying to conncet to target device");
				this.Close();
				return;
			}

			this.startProtocol();

		}

		private void menuExit_Click(object sender, EventArgs e)
		{
			this.Close();
		}

		private byte[] receiveBytes(int amount)
		{
			int read = 0;
			byte[] data = new byte[amount];
			while (read < amount)
			{
				read += this.sock.Read(data, read, amount - read);
				if (read == 0)
				{
					MessageBox.Show("Read " + read + "bytes");
				}
			}
			return data;
		}

		private int receiveInt()
		{
			int read = 0;
			byte[] data = new byte[4];
			while (read < 4)
			{
				read += this.sock.Read(data, read, 4-read);
				if (read == 0)
				{
					MessageBox.Show("Read " + read + "bytes");
				}
			}
			return IPAddress.NetworkToHostOrder(BitConverter.ToInt32(data, 0));
		}

		private void sendInt(int value)
		{
			byte[] data = BitConverter.GetBytes(
				IPAddress.HostToNetworkOrder(value)
			);
			this.sock.Write(data, 0, data.Length);
		}

		private void startProtocol()
		{
			sendInt(ProtocolVersion);
			sendInt(PacketHello);
			sendInt(this.pictureBox.Width);
			sendInt(this.pictureBox.Height);

			int version = receiveInt();
			if (version > ProtocolVersion)
			{
				throw new Exception("Unsupported server version: " + version);
			}

			if (receiveInt() != PacketHello)
			{
				throw new Exception("Unexpected packet received");
			}

			protocolThread = new Thread(this.Protocol);
			protocolThread.Start();

		}

		private delegate void showErrorDelegate(string err);
		private delegate void setImageDelegate(Image img);
		private delegate void setNotesDelegate(string notes);

		private void setImage(Image img)
		{
			if (this.InvokeRequired)
			{
				Invoke(new setImageDelegate(this.setImage), img);
			}
			else
			{
				this.currentSlide = img;
				this.pictureBox.Image = img;
			}
		}

		private void setNotes(string notes)
		{
			if (this.InvokeRequired)
			{
				Invoke(new setNotesDelegate(this.setNotes), notes);
			}
			else
			{
				this.currentNotes = notes;
				this.textNotes.Text = notes;
			}
		}

		private void showError(string err)
		{
			if (this.InvokeRequired)
			{
				Invoke(new showErrorDelegate(this.showError), err);
			}
			else
			{
				MessageBox.Show("Error: " + err);
			}
		}

		private void Protocol()
		{
			int size;

			while (!finishThread)
			{
				try
				{
					int type = this.receiveInt();
					switch (type)
					{

						case PacketCurrentSlide:
							size = this.receiveInt();
							int pageNum = this.receiveInt();
							System.IO.MemoryStream stream = new System.IO.MemoryStream(receiveBytes(size));
							setImage(new Bitmap(stream));
							stream.Close();
							break;

						case PacketNotes:
							size = this.receiveInt();
							byte[] notesData = receiveBytes(size);
							setNotes(Encoding.UTF8.GetString(notesData, 0, notesData.Length).Replace("\n","\r\n"));
							//MessageBox.Show("Notes:" + Encoding.UTF8.GetString(notesData, 0, notesData.Length));
							break;

						default:
							showError("Unknown packet type" + type );
							break;
					}
				}
				catch (Exception ex)
				{
					if (!this.finishThread)
					{
						showError(ex.Message);
						break;
					}
				}
			}
		}

		private void MainForm_Closed(object sender, EventArgs e)
		{

		}

		private void MainForm_Closing(object sender, CancelEventArgs e)
		{
			if (this.protocolThread != null)
			{
				this.sock.Close();
				this.finishThread = true;
				protocolThread.Join(500);
				protocolThread.Abort();
			}
		}

		private void menuPrev_Click(object sender, EventArgs e)
		{
			sendInt(PacketKeyPress);
			sendInt(280);
		}

		private void menuNext_Click(object sender, EventArgs e)
		{
			sendInt(PacketKeyPress);
			sendInt(281);
		}

		private void toggleNotes()
		{
			this.textNotes.Visible = !this.textNotes.Visible;
			this.pictureBox.Visible = !this.pictureBox.Visible;
		}

		private void menuNotes_Click(object sender, EventArgs e)
		{
			toggleNotes();
		}

		private void MainForm_KeyDown(object sender, KeyEventArgs e)
		{
			if ((e.KeyCode == System.Windows.Forms.Keys.Up))
			{
			}
			if ((e.KeyCode == System.Windows.Forms.Keys.Down))
			{
				// Bajar oscilador
				// Bajar
			}
			if ((e.KeyCode == System.Windows.Forms.Keys.Left))
			{
				menuPrev_Click(sender, e);
			}
			if ((e.KeyCode == System.Windows.Forms.Keys.Right))
			{
				menuNext_Click(sender, e);
			}
			if ((e.KeyCode == System.Windows.Forms.Keys.Enter))
			{
				toggleNotes();
			}

		}
	}
}