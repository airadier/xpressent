using System;
using System.Collections.Generic;
using System.Text;
using Microsoft.WindowsMobile.SharedSource.Bluetooth;

namespace xpressent_remote
{
	public class BtDesc
	{
		BluetoothDevice device;

		public BluetoothDevice Device
		{
			get { return this.device; }
		}

		public BtDesc(BluetoothDevice device)
		{
			this.device = device;
		}

		public override string  ToString()
		{
 			 return this.device.Name;
		}
	}
}
