package aimnet.android.xpressent;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.Vector;

import org.apache.http.util.EncodingUtils;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.DialogInterface;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Typeface;
import android.graphics.Paint.Align;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.view.MotionEvent;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.view.View.OnTouchListener;

class BaseClient extends Thread
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
	
	public BaseClient(XPressent manager, DataInputStream inStream, DataOutputStream outStream) {
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
}

public class XPressent extends Activity implements DialogInterface.OnClickListener, OnTouchListener {
    
    static final int DIALOG_SELECTSERVER_ID = 0;
    static final int DIALOG_CONNECTION_ERROR = 1;
    static final int DIALOG_ERROR = 2;

    
	static final int PKT_KEYPRESS = 1;    
    
    static final int MENU_CONNECT = 0;
    static final int MENU_DISCONNECT = 1;
    static final int MENU_EXIT = 99;
    
    Bitmap currSlide;
    Bitmap currNotes;
    float notesOffset;
    float slideOffset;
    boolean showNotes = false;
    String errorMsg;
    
    /* TODO: Remove */
    final CharSequence[] servers = {"10.13.4.3:48151", "10.10.3.3:48151", "Search BT Device", "Enter IP Address"};

    /* The socket that connects to the xpressent server */
	Socket sock;

    public void connectionLost()
    {
    	showDialog(DIALOG_CONNECTION_ERROR);
    	this.sock = null;
    }

    protected void repaintSlide()
    {
    	SurfaceView surfaceView = (SurfaceView) findViewById(R.id.SurfaceView01);
    	SurfaceHolder holder = surfaceView.getHolder();
    	Canvas c = holder.lockCanvas();
    	
    	Paint pClear = new Paint();
    	pClear.setColor(Color.BLACK);
    	c.drawRect(0, 0, 320, 480, pClear);
    	
    	Paint pAlpha = new Paint();
    	pAlpha.setAlpha(this.showNotes ? 50 : 255);
    	c.drawBitmap(this.currSlide, 0 - this.slideOffset, 0, pAlpha);
    	
    	if (this.currNotes != null && this.showNotes) 
    		c.drawBitmap(this.currNotes, 5, 5 - this.notesOffset, null);
    	    	
    	holder.unlockCanvasAndPost(c);    	
    }
    
    public void slideChanged(int page_number, Bitmap slide, String notes)
    {
    	
		this.notesOffset = 0.0f;
		this.slideOffset = 0.0f;
		this.currSlide = slide;
		this.showNotes = false;
				
		if (notes.length() > 0) {
			String[] l = notes.split("\n");
			Vector<String> lines = new Vector<String>();

			Paint p = new Paint();
	    	p.setColor(Color.WHITE);
	    	p.setTextAlign(Align.LEFT);
	    	p.setTypeface(Typeface.DEFAULT);
	    	p.setAntiAlias(true);
	    	p.setTextSize(15.0f);
					
			for (String line : l) {

				String currLine = "";
				String[] words = line.split(" ");					
				for(String word: words)
				{
					int chars = p.breakText(currLine + " " + word, true, 310.0f, null);
					if (chars < (currLine + " " + word).length()) 
					{
						lines.add(currLine);
						currLine = word;
					}
					else currLine += " " + word;
				}
				
				if (currLine.length() > 0)
				{
					lines.add(currLine);
				}
						
	
			}
			
			this.currNotes = Bitmap.createBitmap(310, (int)(((float)lines.size() + 3.0f) * p.getFontMetrics(null)), Bitmap.Config.ARGB_8888);
			Canvas c = new Canvas(this.currNotes);
			
			int y = 0;
			for (String line : lines)
			{
				y += p.getFontMetricsInt(null);
				c.drawText(line, 0, y, p);
			}
		}
		else
		{
			this.currNotes = null;
		
		}
				
		this.repaintSlide();

    }
    
	public void onClick(DialogInterface dialog, int which) {
		
		String[] serverParts;
		
		dialog.dismiss();
		
		removeDialog(DIALOG_SELECTSERVER_ID);
		
		serverParts = servers[which].toString().split(":");
				
		try {
			sock = new Socket(serverParts[0], Integer.parseInt(serverParts[1]));

			DataInputStream is = new DataInputStream(sock.getInputStream());
			DataOutputStream os = new DataOutputStream(sock.getOutputStream());
			
			Thread runThread = new BaseClient(this, is, os);
						
			runThread.start();
			
		} catch (NumberFormatException e) {
			showDialog(DIALOG_CONNECTION_ERROR);
		} catch (UnknownHostException e) {
			showDialog(DIALOG_CONNECTION_ERROR);
		} catch (IOException e) {
			showDialog(DIALOG_CONNECTION_ERROR);
		}		
		
	}
	
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        
    	SurfaceView surfaceView = (SurfaceView) findViewById(R.id.SurfaceView01);
    	surfaceView.setOnTouchListener(this);
        
        sock = null;
    }
    
    @Override
    protected void onDestroy() {
    	super.onDestroy();
    }
	
	
    @Override
	protected void onStart() {
		super.onStart();
		
		if (sock == null) {		
			showDialog(DIALOG_SELECTSERVER_ID);
		}		
				
	}   
    
    @Override
    protected void onPause() {
    	super.onPause();
    }
    
    @Override
    protected void onStop() {
    	super.onStop();
    	
    	if (this.sock != null)
    	{
    		try {
    			if (this.sock != null) this.sock.close();
			} catch (Exception e) { }
    		sock = null;
    	}
    }

    @Override
    public void finish() {
    	super.finish();
    }
    
    @Override
    protected void onResume() {
    	super.onResume();
    }    
    
    
	@Override
	protected Dialog onCreateDialog(int id) {
		Dialog dialog;
		AlertDialog.Builder builder;
		
		switch(id) {
			case DIALOG_SELECTSERVER_ID:
				builder = new AlertDialog.Builder(this);
				
				builder.setTitle("Choose Server");
				builder.setItems(servers, this);
				dialog = builder.create();
				break;
				
			case DIALOG_CONNECTION_ERROR:
				builder = new AlertDialog.Builder(this);
				
				builder.setMessage("Connection error");
				dialog = builder.create();
				break;

			case DIALOG_ERROR:
				builder = new AlertDialog.Builder(this);
				
				builder.setMessage("Error: " + this.errorMsg);
				dialog = builder.create();
				break;
				
				
			default:
				dialog = null;
			
		}
		return dialog;
	}
	
	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		switch (item.getItemId()) {
		case MENU_CONNECT:
			showDialog(DIALOG_SELECTSERVER_ID);
			return true;
		case MENU_DISCONNECT:
			try {
				if (this.sock != null) this.sock.close();
			} catch (Exception e) {}
			this.sock = null;
			return true;
		case MENU_EXIT:
			this.finish();

		}
		
		return false;
	}
	
	@Override
	public boolean onPrepareOptionsMenu(Menu menu) {
		menu.getItem(MENU_CONNECT).setEnabled(this.sock == null);
		menu.getItem(MENU_DISCONNECT).setEnabled(this.sock != null);
		return true;
	}
	
	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		menu.add(0, MENU_CONNECT, 0, "Connect");
		menu.add(0, MENU_DISCONNECT, 0, "Disconnect");
		menu.add(0, MENU_EXIT, 0, "Exit");
		return true;
	}

	public void sendKeyPress(int value)
	{
		try {
		DataOutputStream os = new DataOutputStream(sock.getOutputStream());
		os.writeInt(PKT_KEYPRESS);
		os.writeInt(4);
		os.writeInt(value);
		}
		catch (Exception ex)
		{
			try {
				this.sock.close();
			} catch (Exception e) {}
			this.connectionLost();
		
		}

	}
	
	float startX, prevY, yMov;
	
	public boolean onTouch(View v, MotionEvent event) {
		
		if (event.getAction() == MotionEvent.ACTION_DOWN)
		{
			startX = event.getX();
			prevY = event.getY();
			yMov = 0;
			return true;
		}
		
		if (event.getAction() == MotionEvent.ACTION_UP)
		{

			
			this.slideOffset = 0;
			if  (event.getEventTime() - event.getDownTime() < 500) {			
				if ((startX - event.getX()) > 160) 
				{
					this.sendKeyPress(281);	
				}
				else if ((event.getX() - startX) > 160) 
				{
					this.sendKeyPress(280);
				}
				else if (Math.abs(event.getX() - startX) < 16 && yMov < 16)
					this.showNotes = !this.showNotes;
			}
			this.repaintSlide();
			return true;
		}
		
		
		if (event.getAction() == MotionEvent.ACTION_MOVE)
		{
			this.slideOffset = startX - event.getX();
			yMov += Math.abs(prevY - event.getY());
			this.notesOffset += prevY - event.getY();
			prevY = event.getY();
			
			if (this.currNotes != null && this.notesOffset > (this.currNotes.getHeight() - 420))
			{
				this.notesOffset = this.currNotes.getHeight() - 420;
			}
			if (this.notesOffset < 0) {
				this.notesOffset = 0;
			}
			
			
			this.repaintSlide();
			
		}

		
		return true;
	}
	
}	