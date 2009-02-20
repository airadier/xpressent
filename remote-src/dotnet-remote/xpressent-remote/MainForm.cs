using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using Microsoft.WindowsMobile.SharedSource.Bluetooth;

namespace xpressent_remote
{
	public partial class MainForm : Form
	{
		XProtocol protocol;

		public MainForm()
		{
			InitializeComponent();
		}

		protected void selectDevice()
		{
			if (this.protocol != null) this.protocol.Disconnect();

			BluetoothDevice btDev = SelectDevice.Run();

			if (btDev != null)
			{
				this.protocol = new XProtocol(btDev, this.pictureBox.Width, this.pictureBox.Height);
				this.protocol.ErrorRaised += this.showError;
				this.protocol.CurrentSlideReceived += this.setSlide;
				this.protocol.Connect();
			}

		}

		private delegate void showErrorDelegate(string err);
		private delegate void setSlideDelegate(int pageNum, Bitmap img, string notes);

		private void setSlide(int pageNum, Bitmap img, string notes)
		{
			if (this.InvokeRequired)
			{
				Invoke(new setSlideDelegate(this.setSlide), pageNum, img, notes);
			}
			else
			{
				this.pictureBox.Image = img;
				this.pictureBox.Text = notes;
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

		private void MainForm_Load(object sender, EventArgs e)
		{
			selectDevice();
		}

		private void menuExit_Click(object sender, EventArgs e)
		{
			this.Close();
		}

		private void MainForm_Closing(object sender, CancelEventArgs e)
		{
			if (this.protocol != null) this.protocol.Disconnect();
		}

		private void menuPrev_Click(object sender, EventArgs e)
		{
			if (this.protocol != null)
				this.protocol.SendKey(280);
		}

		private void menuNext_Click(object sender, EventArgs e)
		{
			if (this.protocol != null)
				this.protocol.SendKey(281);
		}

		private void toggleNotes()
		{
			this.pictureBox.ShowNotes = !this.pictureBox.ShowNotes;
		}


		private void MainForm_KeyDown(object sender, KeyEventArgs e)
		{
			if ((e.KeyCode == System.Windows.Forms.Keys.Up))
			{
				this.pictureBox.TextSize++;
			}
			if ((e.KeyCode == System.Windows.Forms.Keys.Down))
			{
				this.pictureBox.TextSize--;
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

		private void menuNotes_Click(object sender, EventArgs e)
		{
			toggleNotes();
		}

		private void menuPaint_Click(object sender, EventArgs e)
		{
			MessageBox.Show("Not implemented");
		}

		private void menuItem2_Click(object sender, EventArgs e)
		{
			selectDevice();
		}

		private void pictureBox_NextEvent()
		{
			this.menuNext_Click(null, null);
		}

		private void pictureBox_PrevEvent()
		{
			this.menuPrev_Click(null, null);
		}


	}
}