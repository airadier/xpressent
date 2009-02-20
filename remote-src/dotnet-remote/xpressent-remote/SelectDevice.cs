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
	public partial class SelectDevice : Form
	{
		BluetoothRadio btRadio;
		public BtDesc SelectedDevice
		{
			get { return (BtDesc)this.listDevices.SelectedItem; }
		}

		public SelectDevice()
		{
			InitializeComponent();
		}

		public static BluetoothDevice Run()
		{
			SelectDevice dialog = new SelectDevice();
			if (dialog.ShowDialog() != DialogResult.OK) return null;
			if (dialog.SelectedDevice == null) return null;
			return dialog.SelectedDevice.Device;
		}

		private void SelectDevice_Load(object sender, EventArgs e)
		{
			this.btRadio = new BluetoothRadio();
			updateDevices();
		}

		private void updateDevices()
		{
			this.listDevices.Items.Clear();
			try
			{
				foreach (BluetoothDevice btDevice in btRadio.PairedDevices)
				{
					BtDesc desc = new BtDesc(btDevice);
					this.listDevices.Items.Add(desc);
				}
			}
			catch { }
		}

		private void menuItem2_Click(object sender, EventArgs e)
		{
			if (this.listDevices.SelectedIndex < 0) return;
			this.DialogResult = DialogResult.OK;
		}

		private void menuItem1_Click(object sender, EventArgs e)
		{
			this.DialogResult = DialogResult.Cancel;
		}



	}
}