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
