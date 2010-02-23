package aimnet.android.xpressent;

import java.io.IOException;
import java.net.Socket;
import java.net.SocketAddress;
import java.net.UnknownHostException;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.DialogInterface;
import android.os.Bundle;

public class XPressent extends Activity implements DialogInterface.OnClickListener {
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
    }
    
    static final int DIALOG_SELECTSERVER_ID = 0;
    static final int DIALOG_CONNECTION_ERROR = 1;
    
    final CharSequence[] servers = {"BT: xx:xx:xx:xx:xx", "10.13.4.3:48151", "Enter IP Address"};

    
	public void onClick(DialogInterface dialog, int which) {
		
		Socket sock;
		String[] serverParts;
		
		dialog.dismiss();
		removeDialog(DIALOG_SELECTSERVER_ID);
		
		serverParts = servers[which].toString().split(":");
				
		try {
			sock = new Socket(serverParts[0], Integer.parseInt(serverParts[1]));
			sock.close();
			
		} catch (NumberFormatException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			showDialog(DIALOG_CONNECTION_ERROR);
		} catch (UnknownHostException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			showDialog(DIALOG_CONNECTION_ERROR);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			showDialog(DIALOG_CONNECTION_ERROR);
		}
		
		
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
				
			default:
				dialog = null;
			
		}
		return dialog;
	}
	
    @Override
	protected void onStart() {
		super.onStart();
		
		showDialog(DIALOG_SELECTSERVER_ID);
		
	}

		
		
    @Override
    protected void onPause() {
    	super.onPause();
    }
    
    @Override
    protected void onResume() {
    	// TODO Auto-generated method stub
    	super.onResume();
    }
}	