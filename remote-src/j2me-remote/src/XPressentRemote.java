// Copyright 2009, Alvaro J. Iradier
// This file is part of xPressent (J2ME Remote controller).
//
// xPressent is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// xPressent is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with xPressent.  If not, see <http://www.gnu.org/licenses/>.


/*
// jsr082 API
import javax.bluetooth.BluetoothStateException;
import javax.bluetooth.DataElement;
import javax.bluetooth.DeviceClass;
import javax.bluetooth.DiscoveryAgent;
import javax.bluetooth.DiscoveryListener;
import javax.bluetooth.LocalDevice;
import javax.bluetooth.RemoteDevice;
import javax.bluetooth.ServiceRecord;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Vector;


*/

//import javax.bluetooth.UUID;

import javax.microedition.lcdui.*;
import javax.microedition.midlet.MIDlet;



/**
 * Initialize BT device, search for BT services,
 * presents them to user and picks his/her choice,
 * finally download the choosen image and present
 * it to user.
 *
 * @version ,
 */
public class XPressentRemote extends MIDlet implements CommandListener {
    
    /** Describes this server */
    //private static final UUID XPRESSENT_SERVER_UUID =
    //    new UUID("829ABC54A67D0E10BA6700BC59A5CE41", false);

    private static final Command CMD_CANCEL = new Command("Exit", Command.EXIT, 1);
    private static final Command CMD_CONNECT = new Command("Connect", Command.CONNECT, 2);
        
    private Display display;
    private boolean firstTime;
    private Form mainForm;
    
    public XPressentRemote() {
        firstTime = true;
        mainForm = new Form("xPressent Remote");
    }    
    
    protected void startApp() {
        if (firstTime) {
            display = Display.getDisplay(this);

            //mainForm.append(new TextField("Upper Item", null, 10, 0));
            //mainForm.append(new Table("Table", Display.getDisplay(this)));
            //mainForm.append(new TextField("Lower Item", null, 10, 0));
            mainForm.addCommand(CMD_CANCEL);
            mainForm.setCommandListener(this);
            firstTime = false;
        }

        display.setCurrent(mainForm);            
    }
    
    public void commandAction(Command c, Displayable d) {
        if (c == CMD_CANCEL) {
            destroyApp(false);
            notifyDestroyed();
        }
    }

    protected void destroyApp(boolean unconditional) {
    }

    protected void pauseApp() {
    }

}
