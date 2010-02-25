package aimnet.android.xpressent;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.Vector;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.DialogInterface;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Typeface;
import android.graphics.Paint.Align;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.MotionEvent;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.View;
import android.view.View.OnTouchListener;


public class XPressent extends Activity implements DialogInterface.OnClickListener, OnTouchListener {
    
    static final int DIALOG_SELECTSERVER_ID = 0;
    static final int DIALOG_CONNECTION_ERROR = 1;
    static final int DIALOG_ERROR = 2;

    
	static final int PKT_KEYPRESS = 1;    
    
    static final int MENU_CONNECT = 0;
    static final int MENU_DISCONNECT = 1;
    static final int MENU_NEXT = 2;
    static final int MENU_PREV = 3;
    static final int MENU_EXIT = 99;
    
    XPClient xpClient;
    String notes;
    Bitmap currSlide;
    Bitmap currNotes;
    float notesOffset;
    float slideOffset;
    boolean showNotes = false;
    String errorMsg;
	float startX, prevY, yMov;
	float fontSize = 15.0f;
	int windowWidth, windowHeight;
    
    /* TODO: Remove */
    final CharSequence[] servers = {"10.13.4.3:48151", "10.10.3.3:48151", "Search BT Device", "Enter IP Address"};

    /* The socket that connects to the xpressent server */
	Socket sock;

    public void connectionLost()
    {
    	showDialog(DIALOG_CONNECTION_ERROR);
    	this.sock = null;
    }
    
    protected void repaintNotes()
    {
		if (notes.length() > 0) {
			String[] l = notes.split("\n");
			Vector<String> lines = new Vector<String>();

			Paint p = new Paint();
	    	p.setColor(Color.WHITE);
	    	p.setTextAlign(Align.LEFT);
	    	p.setTypeface(Typeface.DEFAULT);
	    	p.setAntiAlias(true);
	    	p.setTextSize(this.fontSize);
	    						
			for (String line : l) {

				String currLine = "";
				String[] words = line.split(" ");					
				for(String word: words)
				{
					int chars = p.breakText(currLine + " " + word, true, this.windowWidth - 10, null);
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
			
			this.currNotes = Bitmap.createBitmap(this.windowWidth -10, (int)(((float)lines.size() + 3.0f) * p.getFontMetrics(null)), Bitmap.Config.ARGB_8888);
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
    }
    
    
    protected void repaintSlide()
    {
    	SurfaceView surfaceView = (SurfaceView) findViewById(R.id.SurfaceView01);
    	SurfaceHolder holder = surfaceView.getHolder();
    	Canvas c = holder.lockCanvas();
    	
    	this.windowWidth = c.getWidth();
    	this.windowHeight = c.getHeight();
    	
    	if (this.currNotes == null)
    		this.repaintNotes();
    	
    	Paint pClear = new Paint();
    	pClear.setColor(Color.BLACK);
    	c.drawRect(0, 0, c.getWidth(), c.getHeight(), pClear);
    	
    	Paint pAlpha = new Paint();
    	pAlpha.setAlpha(this.showNotes ? 60 : 255);
    	c.drawBitmap(this.currSlide, 0 - this.slideOffset, (c.getHeight() - this.currSlide.getHeight()) / 2, pAlpha);
    	
    	if (this.currNotes != null && this.showNotes) 
    		c.drawBitmap(this.currNotes, 5, 5 - this.notesOffset, null);
    	    	
    	holder.unlockCanvasAndPost(c);    	
    }
    
    public void slideChanged(int page_number, Bitmap slide, String notes)
    {
    	
		this.notesOffset = 0.0f;
		this.slideOffset = 0.0f;
		this.currSlide = slide;
		this.currNotes = null;
		this.notes = notes;
		this.showNotes = false;
		
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
			
			xpClient = new XPClient(this, is, os);
						
			xpClient.start();
			
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
		menu.add(0, MENU_NEXT, 0, "Next");
		menu.add(0, MENU_PREV, 0, "Prev.");
		menu.add(0, MENU_EXIT, 0, "Exit");
		return true;
	}	
	
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
				if ((startX - event.getX()) > (this.windowWidth / 2)) 
				{
					xpClient.sendKeyPress(281);	
				}
				else if ((event.getX() - startX) > (this.windowWidth / 2)) 
				{
					xpClient.sendKeyPress(280);
				}
				else if (Math.abs(event.getX() - startX) < (this.windowWidth/20) && yMov < (this.windowHeight/20))
					this.showNotes = !this.showNotes;
			}
			this.repaintSlide();
			return true;
		}
		
		
		if (event.getAction() == MotionEvent.ACTION_MOVE)
		{
			this.slideOffset = startX - event.getX();
			
			yMov += Math.abs(prevY - event.getY());
			//this.notesOffset += prevY - event.getY();
			
			this.moveNotes(prevY - event.getY());

			prevY = event.getY();
						
		}

		
		return true;
	}
	
	public void moveNotes(float offset)
	{
		this.notesOffset += offset;
		
		if (this.currNotes != null && this.notesOffset > (this.currNotes.getHeight() - this.windowHeight))
		{
			this.notesOffset = this.currNotes.getHeight() - this.windowHeight;
		}
		if (this.notesOffset < 0) {
			this.notesOffset = 0;
		}
		
		
		this.repaintSlide();

	}
	
    @Override
    public boolean onTrackballEvent(MotionEvent event) {
    	if (event.getY() != 0) {
    		this.moveNotes(event.getY() * 2 * this.fontSize);
    		return true;
    	}
    	
    	return false;
    }
    
    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
    	if (keyCode == KeyEvent.KEYCODE_DPAD_DOWN) {
    		this.moveNotes(2 * this.fontSize);
    		return true;
    	} 
    	else if (keyCode == KeyEvent.KEYCODE_DPAD_UP) {
    		this.moveNotes(-2 * this.fontSize);
    		return true;
    	} 
    	else if (keyCode == KeyEvent.KEYCODE_DPAD_CENTER)
    	{
			this.showNotes = !this.showNotes;
			this.repaintSlide();
			return true;
    	}
    	else if (keyCode == KeyEvent.KEYCODE_VOLUME_UP) {
    		this.fontSize += 1.0f;
    		this.repaintNotes();
    		this.repaintSlide();
    		return true;
    	} 
    	else if (keyCode == KeyEvent.KEYCODE_VOLUME_DOWN) {
    		this.fontSize -= 1.0f;
    		this.repaintNotes();
    		this.repaintSlide();
    		return true;
    	} 
    	
    	return false;
    }
	
	
}	