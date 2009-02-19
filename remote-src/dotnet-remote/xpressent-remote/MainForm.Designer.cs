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
			this.menuPaint = new System.Windows.Forms.MenuItem();
			this.menuItem1 = new System.Windows.Forms.MenuItem();
			this.menuPrev = new System.Windows.Forms.MenuItem();
			this.menuNext = new System.Windows.Forms.MenuItem();
			this.menuNotes = new System.Windows.Forms.MenuItem();
			this.menuExit = new System.Windows.Forms.MenuItem();
			this.pictureBox = new xpressent_remote.TextPictureBox();
			this.pictureBox1 = new System.Windows.Forms.PictureBox();
			this.pictureBox2 = new System.Windows.Forms.PictureBox();
			this.SuspendLayout();
			// 
			// mainMenu
			// 
			this.mainMenu.MenuItems.Add(this.menuPaint);
			this.mainMenu.MenuItems.Add(this.menuItem1);
			this.mainMenu.MenuItems.Add(this.menuExit);
			// 
			// menuPaint
			// 
			this.menuPaint.Text = "Paint";
			this.menuPaint.Click += new System.EventHandler(this.menuPaint_Click);
			// 
			// menuItem1
			// 
			this.menuItem1.MenuItems.Add(this.menuPrev);
			this.menuItem1.MenuItems.Add(this.menuNext);
			this.menuItem1.MenuItems.Add(this.menuNotes);
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
			// menuNotes
			// 
			this.menuNotes.Text = "Toggle Notes";
			this.menuNotes.Click += new System.EventHandler(this.menuNotes_Click);
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
			this.pictureBox.Image = ((System.Drawing.Bitmap)(resources.GetObject("pictureBox.Image")));
			this.pictureBox.Location = new System.Drawing.Point(0, 0);
			this.pictureBox.Name = "pictureBox";
			this.pictureBox.Size = new System.Drawing.Size(240, 268);
			this.pictureBox.TabIndex = 0;
			// 
			// pictureBox1
			// 
			this.pictureBox1.Image = ((System.Drawing.Image)(resources.GetObject("pictureBox1.Image")));
			this.pictureBox1.Location = new System.Drawing.Point(205, 233);
			this.pictureBox1.Name = "pictureBox1";
			this.pictureBox1.Size = new System.Drawing.Size(32, 32);
			this.pictureBox1.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage;
			// 
			// pictureBox2
			// 
			this.pictureBox2.Image = ((System.Drawing.Image)(resources.GetObject("pictureBox2.Image")));
			this.pictureBox2.Location = new System.Drawing.Point(3, 233);
			this.pictureBox2.Name = "pictureBox2";
			this.pictureBox2.Size = new System.Drawing.Size(32, 32);
			this.pictureBox2.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage;
			// 
			// MainForm
			// 
			this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.None;
			this.ClientSize = new System.Drawing.Size(240, 268);
			this.Controls.Add(this.pictureBox2);
			this.Controls.Add(this.pictureBox1);
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
		private System.Windows.Forms.PictureBox pictureBox1;
		private System.Windows.Forms.PictureBox pictureBox2;
	}
}

