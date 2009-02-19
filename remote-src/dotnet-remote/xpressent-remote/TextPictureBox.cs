using System;
using System.Collections.Generic;
using System.Text;
using System.Drawing;
using System.Drawing.Imaging;
using System.Windows.Forms;

namespace xpressent_remote
{
	public class TextPictureBox: Control
	{

		Bitmap offscreen = null;
		Bitmap image, darkImage;
		Bitmap notesBitmap;
		string notes = "";
		int textSize = 11;
		int notesOffset;
		int lastMousePos;
		bool showNotes;
		bool dragging = false;
		bool dragged = false;

		public Bitmap Image
		{
			get { return this.image; }
			set {
				this.image = value;
				if (value != null)
				{
					this.darkImage = AdjustBrightness(this.Image, 10);
				}
				else
				{
					this.darkImage = null;
				}

				DrawNotes();
				DrawOffscreen();
				this.Invalidate();
			}
		}

		public new string Text
		{
			get { return this.notes; }
			set
			{
				this.notes = value;
				this.notesOffset = 0;
				DrawNotes();
				DrawOffscreen();
				this.Invalidate();
			}

		}

		public bool ShowNotes
		{
			get { return this.showNotes; }
			set { 
				this.showNotes = value;
				DrawNotes();
				DrawOffscreen();
				this.Invalidate();
			}
		}

		public int TextSize
		{
			get { return this.textSize; }
			set {
				if (value < 1) return;
				this.textSize = value;
				DrawNotes();
				DrawOffscreen();
				this.Invalidate();
			}
		}


		private struct PixelData
		{
			public byte Blue;
			public byte Green;
			public byte Red;
		}


		public TextPictureBox()
			: base()
		{
			this.InitializeComponent();
		}

		private string[] splitLines(Graphics g, Font f, string text, int maxwidth)
		{
			List<string> lines = new List<string>();

			foreach (string line in text.Split('\n'))
			{
				string current_line = "";
				foreach (string word in line.Split(' '))
				{
					SizeF size = g.MeasureString(current_line + " " + word, f);
					if (size.Width > maxwidth)
					{
						lines.Add(current_line);
						current_line = "";
					}
					current_line += word + " ";
				}
				lines.Add(current_line);
			}

			return lines.ToArray();
		}

		private void DrawNotes()
		{
			Graphics g = this.CreateGraphics();
			Font font = new Font(FontFamily.GenericSansSerif, this.textSize, 0);
			string[] textLines = splitLines(g, font, this.notes ?? "", this.Width - 10);

			string text = String.Join("\n", textLines);
			if (this.notesBitmap != null) this.notesBitmap.Dispose();
			this.notesBitmap = new Bitmap(this.Width - 10, (int)g.MeasureString(text, font).Height);
			g.Dispose();

			Graphics g2 = Graphics.FromImage(this.notesBitmap);
			g2.DrawString(text, font, new SolidBrush(Color.White), 0, 0);
			g2.Dispose();

		}

		private void DrawOffscreen()
		{

			if (this.offscreen == null) offscreen = new Bitmap(this.Width, this.Height);
			
			Bitmap off = this.offscreen;
			Graphics g = Graphics.FromImage(off);

			g.FillRectangle(new SolidBrush(Color.Black), 0,0, off.Width, off.Height);

			if (this.showNotes)
			{
				if (this.darkImage != null)
				{
					g.DrawImage(this.darkImage,
						(off.Width - this.darkImage.Width) / 2,
						(off.Height - this.darkImage.Height) / 2);
				}
				if (this.notesBitmap == null)
				{
					DrawNotes();
				}

				ImageAttributes attr = new ImageAttributes();
				attr.SetColorKey(Color.Black, Color.Black);
				g.DrawImage(this.notesBitmap,
					new Rectangle(5,5 + this.notesOffset, this.notesBitmap.Width, this.notesBitmap.Height),
					0, 0, this.notesBitmap.Width, this.notesBitmap.Height, GraphicsUnit.Pixel,attr);
			}
			else
			{
				if (this.image != null)
				{
					g.DrawImage(this.image,
						(off.Width - this.image.Width) / 2,
						(off.Height - this.image.Height) / 2);
				}
			}

		}

		protected override void OnPaint(PaintEventArgs e)
		{
			if (this.offscreen == null) DrawOffscreen();
			e.Graphics.DrawImage(this.offscreen, 0, 0);
		}

		protected override void OnPaintBackground(PaintEventArgs e)
		{
		}


		private static unsafe Bitmap AdjustBrightness(Bitmap Bitmap, decimal Percent)
		{

			Percent /= 100;
			Bitmap Snapshot = (Bitmap)Bitmap.Clone();
			Rectangle rect = new Rectangle(0, 0, Bitmap.Width, Bitmap.Height);

			BitmapData BitmapBase = Snapshot.LockBits(rect, ImageLockMode.ReadWrite, PixelFormat.Format24bppRgb);
			byte* BitmapBaseByte = (byte*)BitmapBase.Scan0.ToPointer();

			// the number of bytes in each row of a bitmap is allocated (internally) to be equally divisible by 4
			int RowByteWidth = rect.Width * 3;
			if (RowByteWidth % 4 != 0)
			{
				RowByteWidth += (4 - (RowByteWidth % 4));
			}

			for (int i = 0; i < RowByteWidth * rect.Height; i += 3)
			{
				PixelData* p = (PixelData*)(BitmapBaseByte + i);

				p->Red = (byte)Math.Round(Math.Min(p->Red * Percent, (decimal)255));
				p->Green = (byte)Math.Round(Math.Min(p->Green * Percent, (decimal)255));
				p->Blue = (byte)Math.Round(Math.Min(p->Blue * Percent, (decimal)255));
			}

			Snapshot.UnlockBits(BitmapBase);
			return Snapshot;
		}

		private void InitializeComponent()
		{
			this.SuspendLayout();
			// 
			// TextPictureBox
			// 
			this.MouseMove += new System.Windows.Forms.MouseEventHandler(this.TextPictureBox_MouseMove);
			this.MouseDown += new System.Windows.Forms.MouseEventHandler(this.TextPictureBox_MouseDown);
			this.Resize += new System.EventHandler(this.TextPictureBox_Resize);
			this.MouseUp += new System.Windows.Forms.MouseEventHandler(this.TextPictureBox_MouseUp);
			this.ResumeLayout(false);

		}

		private void TextPictureBox_MouseDown(object sender, MouseEventArgs e)
		{
			if (e.Button == MouseButtons.Left) this.dragging = true;
			this.dragged = false;
			this.lastMousePos = e.Y;
		}

		private void TextPictureBox_MouseUp(object sender, MouseEventArgs e)
		{
			if (e.Button == MouseButtons.Left) this.dragging = false;
			if (!this.dragged) this.ShowNotes = !this.ShowNotes;
		}

		private void TextPictureBox_MouseMove(object sender, MouseEventArgs e)
		{
			if (e.Y != this.lastMousePos) this.dragged = true;
			if (!this.dragging || !this.showNotes || this.notesBitmap == null) return;

			this.notesOffset += e.Y - this.lastMousePos;
			if (notesOffset > 0) this.notesOffset = 0;
			if (notesOffset < 0 - this.notesBitmap.Height) notesOffset = 0 - this.notesBitmap.Height;
			this.lastMousePos = e.Y;

			DrawOffscreen();
			this.Invalidate();
		}

		private void TextPictureBox_Resize(object sender, EventArgs e)
		{
			this.offscreen.Dispose();
			this.offscreen = null;
			this.DrawNotes();
			this.DrawOffscreen();
			this.Invalidate();
		}

	}
}
