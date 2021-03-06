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
		Icon prevBitmap, nextBitmap;
		string notes = "";
		int textSize = 11;
		int notesOffset;
		int lastMousePos;
		bool showNotes;
		bool dragging = false;
		bool dragged = false;

		public delegate void NextPrevEventDelegate();
		public event NextPrevEventDelegate NextEvent;
		public event NextPrevEventDelegate PrevEvent;

		public Bitmap Image
		{
			get { return this.image; }
			set {
				this.image = value;
				if (value != null)
				{
					this.darkImage = AdjustBrightness(this.Image, 20);
				}
				else
				{
					this.darkImage = null;
				}
				DrawOffscreen();
				this.Invalidate();
			}
		}

		public new string Text
		{
			get { return this.notes; }
			set
			{
				this.notes = value.Replace("\r", "");
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
				this.Refresh();
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
				this.Refresh();
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

		private string[] splitLines(Graphics g, Font f, Font ff, string text, int maxwidth, out int height)
		{
            bool fixed_mode = false;
			List<string> lines = new List<string>();
            height = 0;

			foreach (string line in text.Split('\n'))
			{

                if (fixed_mode)
                {
                    if (line.CompareTo("}") == 0)
                    {
                        fixed_mode = false;
                        lines.Add(line);
                        continue;
                    }

                    lines.Add(line);
                    height += (int)g.MeasureString(line, ff).Height;
                }
                else
                {
                    if (line.CompareTo("{") == 0)
                    {
                        fixed_mode = true;
                        lines.Add(line);
                        continue;
                    }

				    string current_line = "";
				    foreach (string word in line.Split(' '))
				    {
					    SizeF size = g.MeasureString(current_line + word, f);
					    if (size.Width > maxwidth)
					    {
                            string prev_line = current_line;
						    lines.Add(current_line);
                            height += (int)g.MeasureString(current_line, f).Height;
						    current_line = "";
                            for (int i = 0; i < prev_line.Length; i++)
                            {
                                if (prev_line[i] == ' ' || prev_line[i] == '-' || prev_line[i] == '*')
                                {
                                    current_line += " ";
                                }
                                else
                                {
                                    break;
                                }
                            }
					    }
					    current_line += word + " ";
				    }
				    lines.Add(current_line);
                    height += (int)g.MeasureString(current_line, f).Height;
                }

			}

			return lines.ToArray();
		}

		private void DrawNotes()
		{
			Graphics g = this.CreateGraphics();
			Font font = new Font(FontFamily.GenericSansSerif, this.textSize, 0);
            Font fixed_font = new Font(FontFamily.GenericMonospace, this.textSize, 0);
            int total_height = 0;
			string[] textLines = splitLines(g, font, fixed_font, this.notes ?? "", this.Width - 10, out total_height);

            if (this.notesBitmap != null) this.notesBitmap.Dispose();
			this.notesBitmap = new Bitmap(this.Width - 10, total_height);
            g.Dispose();
            Graphics g2 = Graphics.FromImage(this.notesBitmap);
            float y = 0;
            bool fixed_mode = false;
            foreach (string line in textLines) 
            {
                if (fixed_mode)
                {
                    if (line.CompareTo("}") == 0)
                    {
                        fixed_mode = false;
                        continue;
                    }

                    g2.DrawString(line, fixed_font, new SolidBrush(Color.White), 0, y);
                    y += g2.MeasureString(line, fixed_font).Height;
                }
                else
                {
                    if (line.CompareTo("{") == 0)
                    {
                        fixed_mode = true;
                        continue;
                    }

                    g2.DrawString(line, font, new SolidBrush(Color.White), 0, y);
                    y += g2.MeasureString(line, font).Height;
                }
            }
            g2.Dispose();

		}

		private void DrawOffscreen()
		{

			if (this.offscreen == null)
			{
				this.offscreen = new Bitmap(this.Width, this.Height);
			}
			
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

			g.DrawIcon(this.prevBitmap, 0, this.Height - this.prevBitmap.Height);
			g.DrawIcon(this.nextBitmap, this.Width - this.nextBitmap.Width, this.Height - this.nextBitmap.Height);

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

			System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(TextPictureBox));
			prevBitmap = (Icon)resources.GetObject("left_arrow_icon");
			nextBitmap = (Icon)resources.GetObject("right_arrow_icon");

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

            if (e.Button == MouseButtons.Left && !this.dragged)
            {
                this.dragging = true;
                this.lastMousePos = e.Y;
            }
            else
            {
                this.dragging = false;
            }
            
		}

		private void TextPictureBox_MouseUp(object sender, MouseEventArgs e)
		{

            if (e.Button == MouseButtons.Left)
            {
                this.dragging = false;
                this.lastMousePos = -1;
                if (!this.dragged)
                {
                    if (e.Y >= (this.Height - this.prevBitmap.Height) &&
                        e.X <= this.prevBitmap.Width)
                    {
                        if (this.PrevEvent != null) this.PrevEvent();
                    }
                    else if (e.Y >= (this.Height - this.nextBitmap.Height) &&
                        e.X >= this.Width - this.nextBitmap.Width)
                    {
                        if (this.NextEvent != null) this.NextEvent();
                    }
                    else
                    {
                        this.ShowNotes = !this.ShowNotes;
                    }
                }
            }

            this.dragged = false;

		}

		private void TextPictureBox_MouseMove(object sender, MouseEventArgs e)
		{
            if (this.dragging && (e.Y < this.lastMousePos - 3 || e.Y > this.lastMousePos + 3))
            {
                this.dragged = true;
            }

            if (this.dragging && this.dragged)
            {
                if (!this.showNotes || this.notesBitmap == null) return;

                this.notesOffset += e.Y - this.lastMousePos;
                if (notesOffset > 0) this.notesOffset = 0;
                if (notesOffset < 0 - this.notesBitmap.Height) notesOffset = 0 - this.notesBitmap.Height;
                this.lastMousePos = e.Y;

                DrawOffscreen();
                this.Refresh();
            }
		}

		private void TextPictureBox_Resize(object sender, EventArgs e)
		{
			if (this.offscreen != null)
			{
				this.offscreen.Dispose();
				this.offscreen = null;
			}
			this.DrawNotes();
			this.DrawOffscreen();
			this.Invalidate();
		}

	}
}
