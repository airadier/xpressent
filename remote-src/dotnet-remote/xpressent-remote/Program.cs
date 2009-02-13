using System;
using System.Collections.Generic;
using System.Windows.Forms;

namespace xpressent_remote
{
	static class Program
	{
		/// <summary>
		/// Punto de entrada principal para la aplicación.
		/// </summary>
		[MTAThread]
		static void Main()
		{
			Application.Run(new MainForm());
		}
	}
}