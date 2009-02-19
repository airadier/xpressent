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