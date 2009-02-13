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
			this.menuPrev = new System.Windows.Forms.MenuItem();
			this.menuNext = new System.Windows.Forms.MenuItem();
			this.menuNotes = new System.Windows.Forms.MenuItem();
			this.menuPaint = new System.Windows.Forms.MenuItem();
			this.menuExit = new System.Windows.Forms.MenuItem();
			this.pictureBox = new System.Windows.Forms.PictureBox();
			this.textNotes = new System.Windows.Forms.TextBox();
			this.SuspendLayout();
			// 
			// mainMenu
			// 
			this.mainMenu.MenuItems.Add(this.menuPrev);
			this.mainMenu.MenuItems.Add(this.menuNext);
			this.mainMenu.MenuItems.Add(this.menuNotes);
			this.mainMenu.MenuItems.Add(this.menuPaint);
			this.mainMenu.MenuItems.Add(this.menuExit);
			// 
			// menuPrev
			// 
			this.menuPrev.Text = "Prev";
			this.menuPrev.Click += new System.EventHandler(this.menuPrev_Click);
			// 
			// menuNext
			// 
			this.menuNext.Text = "Next";
			this.menuNext.Click += new System.EventHandler(this.menuNext_Click);
			// 
			// menuNotes
			// 
			this.menuNotes.Text = "Notes";
			this.menuNotes.Click += new System.EventHandler(this.menuNotes_Click);
			// 
			// menuPaint
			// 
			this.menuPaint.Text = "Paint";
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
			this.pictureBox.SizeMode = System.Windows.Forms.PictureBoxSizeMode.CenterImage;
			// 
			// textNotes
			// 
			this.textNotes.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom)
						| System.Windows.Forms.AnchorStyles.Left)
						| System.Windows.Forms.AnchorStyles.Right)));
			this.textNotes.Location = new System.Drawing.Point(0, 0);
			this.textNotes.Multiline = true;
			this.textNotes.Name = "textNotes";
			this.textNotes.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
			this.textNotes.Size = new System.Drawing.Size(240, 268);
			this.textNotes.TabIndex = 1;
			this.textNotes.Text = "textBox1";
			this.textNotes.Visible = false;
			// 
			// MainForm
			// 
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.None;
			this.ClientSize = new System.Drawing.Size(240, 268);
			this.Controls.Add(this.textNotes);
			this.Controls.Add(this.pictureBox);
			this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
			this.KeyPreview = true;
			this.Menu = this.mainMenu;
			this.MinimizeBox = false;
			this.Name = "MainForm";
			this.Text = "xPressent Remote";
			this.Load += new System.EventHandler(this.MainForm_Load);
			this.Closed += new System.EventHandler(this.MainForm_Closed);
			this.Closing += new System.ComponentModel.CancelEventHandler(this.MainForm_Closing);
			this.KeyDown += new System.Windows.Forms.KeyEventHandler(this.MainForm_KeyDown);
			this.ResumeLayout(false);

		}

		#endregion

		private System.Windows.Forms.MenuItem menuPrev;
		private System.Windows.Forms.MenuItem menuNext;
		private System.Windows.Forms.MenuItem menuNotes;
		private System.Windows.Forms.MenuItem menuPaint;
		private System.Windows.Forms.MenuItem menuExit;
		private System.Windows.Forms.PictureBox pictureBox;
		private System.Windows.Forms.TextBox textNotes;
	}
}

