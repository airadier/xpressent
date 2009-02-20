namespace xpressent_remote
{
	partial class MainForm
	{
		/// <summary>
		/// Variable del diseñador requerida.
		/// </summary>
		private System.ComponentModel.IContainer components = null;
		private System.Windows.Forms.MainMenu mainMenu;

		/// <summary>
		/// Limpiar los recursos que se estén utilizando.
		/// </summary>
		/// <param name="disposing">true si los recursos administrados se deben eliminar; false en caso contrario, false.</param>
		protected override void Dispose(bool disposing)
		{
			if (disposing && (components != null))
			{
				components.Dispose();
			}
			base.Dispose(disposing);
		}

		#region Código generado por el Diseñador de Windows Forms

		/// <summary>
		/// Método necesario para admitir el Diseñador. No se puede modificar
		/// el contenido del método con el editor de código.
		/// </summary>
		private void InitializeComponent()
		{
			System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainForm));
			this.mainMenu = new System.Windows.Forms.MainMenu();
			this.menuItem1 = new System.Windows.Forms.MenuItem();
			this.menuPrev = new System.Windows.Forms.MenuItem();
			this.menuNext = new System.Windows.Forms.MenuItem();
			this.menuItem5 = new System.Windows.Forms.MenuItem();
			this.menuNotes = new System.Windows.Forms.MenuItem();
			this.menuPaint = new System.Windows.Forms.MenuItem();
			this.menuItem3 = new System.Windows.Forms.MenuItem();
			this.menuItem2 = new System.Windows.Forms.MenuItem();
			this.menuItem4 = new System.Windows.Forms.MenuItem();
			this.menuExit = new System.Windows.Forms.MenuItem();
			this.pictureBox = new xpressent_remote.TextPictureBox();
			this.SuspendLayout();
			// 
			// mainMenu
			// 
			this.mainMenu.MenuItems.Add(this.menuItem1);
			this.mainMenu.MenuItems.Add(this.menuItem3);
			// 
			// menuItem1
			// 
			this.menuItem1.MenuItems.Add(this.menuPrev);
			this.menuItem1.MenuItems.Add(this.menuNext);
			this.menuItem1.MenuItems.Add(this.menuItem5);
			this.menuItem1.MenuItems.Add(this.menuNotes);
			this.menuItem1.MenuItems.Add(this.menuPaint);
			this.menuItem1.Text = "Slide";
			// 
			// menuPrev
			// 
			this.menuPrev.Text = "Previous";
			this.menuPrev.Click += new System.EventHandler(this.menuPrev_Click);
			// 
			// menuNext
			// 
			this.menuNext.Text = "Next";
			this.menuNext.Click += new System.EventHandler(this.menuNext_Click);
			// 
			// menuItem5
			// 
			this.menuItem5.Checked = true;
			this.menuItem5.Text = "-";
			// 
			// menuNotes
			// 
			this.menuNotes.Text = "Toggle Notes";
			this.menuNotes.Click += new System.EventHandler(this.menuNotes_Click);
			// 
			// menuPaint
			// 
			this.menuPaint.Text = "Paint";
			this.menuPaint.Click += new System.EventHandler(this.menuPaint_Click);
			// 
			// menuItem3
			// 
			this.menuItem3.MenuItems.Add(this.menuItem2);
			this.menuItem3.MenuItems.Add(this.menuItem4);
			this.menuItem3.MenuItems.Add(this.menuExit);
			this.menuItem3.Text = "Remote";
			// 
			// menuItem2
			// 
			this.menuItem2.Text = "Connect";
			this.menuItem2.Click += new System.EventHandler(this.menuItem2_Click);
			// 
			// menuItem4
			// 
			this.menuItem4.Text = "-";
			// 
			// menuExit
			// 
			this.menuExit.Text = "Exit";
			this.menuExit.Click += new System.EventHandler(this.menuExit_Click);
			// 
			// pictureBox
			// 
			this.pictureBox.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
						| System.Windows.Forms.AnchorStyles.Left)
						| System.Windows.Forms.AnchorStyles.Right)));
			this.pictureBox.Location = new System.Drawing.Point(0, 0);
			this.pictureBox.Name = "pictureBox";
			this.pictureBox.Size = new System.Drawing.Size(240, 268);
			this.pictureBox.TabIndex = 0;
			this.pictureBox.PrevEvent += new xpressent_remote.TextPictureBox.NextPrevEventDelegate(this.pictureBox_PrevEvent);
			this.pictureBox.NextEvent += new xpressent_remote.TextPictureBox.NextPrevEventDelegate(this.pictureBox_NextEvent);
			// 
			// MainForm
			// 
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.None;
			this.ClientSize = new System.Drawing.Size(240, 268);
			this.Controls.Add(this.pictureBox);
			this.ForeColor = System.Drawing.Color.White;
			this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
			this.KeyPreview = true;
			this.Menu = this.mainMenu;
			this.MinimizeBox = false;
			this.Name = "MainForm";
			this.Text = "xPressent Remote";
			this.Load += new System.EventHandler(this.MainForm_Load);
			this.Closing += new System.ComponentModel.CancelEventHandler(this.MainForm_Closing);
			this.KeyDown += new System.Windows.Forms.KeyEventHandler(this.MainForm_KeyDown);
			this.ResumeLayout(false);

		}

		#endregion

		private System.Windows.Forms.MenuItem menuPrev;
		private System.Windows.Forms.MenuItem menuNext;
		private System.Windows.Forms.MenuItem menuExit;
		private TextPictureBox pictureBox;
		private System.Windows.Forms.MenuItem menuPaint;
		private System.Windows.Forms.MenuItem menuItem1;
		private System.Windows.Forms.MenuItem menuNotes;
		private System.Windows.Forms.MenuItem menuItem2;
		private System.Windows.Forms.MenuItem menuItem5;
		private System.Windows.Forms.MenuItem menuItem3;
		private System.Windows.Forms.MenuItem menuItem4;
	}
}

