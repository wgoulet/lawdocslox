package com.lawdocslox.app;
import java.lang.System; 

public class KeyObj {
  private byte[] keyval;
  private int id;


  public KeyObj(byte[] inkeyval,int id) {
    this.keyval = new byte[inkeyval.length];
    System.arraycopy(this.keyval,0,inkeyval,0,inkeyval.length);
  }

  public byte[] getKey() {
    return this.keyval;
  }

}
