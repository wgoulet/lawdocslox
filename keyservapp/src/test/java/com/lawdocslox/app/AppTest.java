package com.lawdocslox.app;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;
import com.lawdocslox.app.KeyObj;
import com.lawdocslox.app.KeyObjFactory;
import java.lang.System;
import org.apache.commons.codec.binary.Base64;

/**
 * Unit test for simple App.
 */
public class AppTest 
    extends TestCase
{
    /**
     * Create the test case
     *
     * @param testName name of the test case
     */
    public AppTest( String testName )
    {
        super( testName );
    }

    /**
     * @return the suite of tests being tested
     */
    public static Test suite()
    {
        return new TestSuite( AppTest.class );
    }

    /**
     * Rigourous Test :-)
     */
    public void testApp()
    {
        // MjE0NTc2NDM=/MTIzNDU2Nw== 
        
        byte[] clientid = Base64.decodeBase64("MjE0NTc2NDM=");
	
        byte[] firmid = Base64.decodeBase64("MTIzNDU2Nw==");

        KeyObj key;
	key = KeyObjFactory.getKeyObj(clientid,firmid);
        for (byte b : key.getKey()) {
            System.out.printf("0x%02X", b);
        }
        System.out.println("Finishing test up!");
        assertTrue( true );
    }
}
