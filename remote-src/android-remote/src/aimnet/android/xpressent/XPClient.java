package aimnet.android.xpressent;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.net.Socket;

import org.apache.http.util.EncodingUtils;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;

public class XPClient extends Thread
{
	XPressent manager;
	Socket sock;
	
	static final int PROT_VERSION = 1;
	static final int PKT_HELLO = 0;
	static final int PKT_KEYPRESS = 1;
	static final int PKT_CURRSLIDE = 2;
	static final int PKT_NEXTSLIDE = 3;
	static final int PKT_PREVSLIDE = 4;
	
	DataInputStream is;
	DataOutputStream os;	
	
	public XPClient(XPressent manager, DataInputStream inStream, DataOutputStream outStream) {
		this.manager = manager;
		this.is = inStream;
		this.os = outStream;
	}
	
	@Override
	public void run() {
		
		try {
			
			os.writeInt(PROT_VERSION);
			os.writeInt(PKT_HELLO);
			os.writeInt(8);
			os.writeInt(320);
			os.writeInt(480);
			os.flush();
			
			if (
				is.readInt() > PROT_VERSION ||
				is.readInt() != PKT_HELLO ||
				is.readInt() != 0
				) throw new Exception("Unexpected greet");
		}
		catch (Exception ex)
		{
			manager.connectionLost();
			return;
		}
		
		while (true)
		{
			try {
				int pkt_type = is.readInt();
				int len = is.readInt();
				
				if (pkt_type == PKT_CURRSLIDE && len > 4)
				{
					int page_number = is.readInt();
					int jpg_len = is.readInt();
					
					byte[] slide_jpg = new byte[jpg_len];
					is.readFully(slide_jpg);
					
					int notes_len = is.readInt();
					String notes = "";
					if (notes_len > 0) 
					{
						byte[] notes_data = new byte[notes_len];
						is.readFully(notes_data);
						notes = EncodingUtils.getString(notes_data,"utf-8");
					}

					Bitmap b = BitmapFactory.decodeByteArray(slide_jpg, 0, slide_jpg.length);
					
					manager.slideChanged(page_number, b, notes);
				}
			} 
			catch (Exception ex)
			{
				this.manager.connectionLost();
				return;
			}
		}
	}
	
	public void sendKeyPress(int value)
	{
		try {
			os.writeInt(PKT_KEYPRESS);
			os.writeInt(4);
			os.writeInt(value);
		}
		catch (Exception ex)
		{
			try {
				this.sock.close();
			} catch (Exception e) {}
			manager.connectionLost();
		
		}

	}
	
}

