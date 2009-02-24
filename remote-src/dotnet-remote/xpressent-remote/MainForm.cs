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
			if (this.protocol != null)
			{
				if (MessageBox.Show(
					"Close current connection?",
					"Now connected",
					MessageBoxButtons.YesNo,
					MessageBoxIcon.Question, MessageBoxDefaultButton.Button1) == DialogResult.No) return;

				this.protocol.Disconnect();
				this.protocol = null;
			}

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
				MessageBox.Show(err, "Error", MessageBoxButtons.OK, MessageBoxIcon.Exclamation, MessageBoxDefaultButton.Button1);
			}
		}

		private void MainForm_Load(object sender, EventArgs e)
		{
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
				this.protocol.NextSlide();
		}

		private void menuNext_Click(object sender, EventArgs e)
		{
			if (this.protocol != null)
				this.protocol.PrevSlide();
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