package com.lawdocslox.app;
import java.lang.System;
import com.lawdocslox.app.KeyObj;

class KeyObjFactory {
    public static KeyObj getKeyObj(byte[] clientid,byte[] firmid) {
        byte[] seed = new byte[clientid.length + firmid.length + 20];
        for(int i = 0; i < seed.length; i++) {
            if(i < clientid.length) {
                seed[i] = clientid[i];
            }
            else if(i < firmid.length + clientid.length) {
                seed[i] = firmid[i - clientid.length];
            }
            else {
                seed[i] = (byte)i;

            }
        } 
        return new KeyObj(seed,10);
    }
}
