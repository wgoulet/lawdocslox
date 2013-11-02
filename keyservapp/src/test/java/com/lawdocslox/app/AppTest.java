package com.lawdocslox.app;

import junit.framework.Test;
import junit.framework.TestCase;
import junit.framework.TestSuite;
import org.junit.Assert;
import com.lawdocslox.app.KeyObj;
import com.lawdocslox.app.KeyObjFactory;
import java.lang.System;
import org.apache.commons.codec.binary.Base64;
import org.bouncycastle.crypto.prng.*;
import org.hamcrest.core.*;

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
     * This test confirms that when same secret and seed value are fed to
     * the KeyObjFactory, the same key is always returned. This test allows
     * us to prove that we'll always generate the same key given the same
     * input.
     */

    public void testConfirmKeySame()
    {
        // MjE0NTc2NDM=/MTIzNDU2Nw== 
        
        byte[] clientid = Base64.decodeBase64("MjE0NTc2NDM=");
	
        byte[] firmid = Base64.decodeBase64("MTIzNDU2Nw==");
	byte[] secret = Base64.decodeBase64("aSBsb3ZlIGplbiEh");
	byte[] seed = new byte[200];
	ThreadedSeedGenerator gen = new ThreadedSeedGenerator();
	seed = gen.generateSeed(200,false);

        KeyObj key,key2;
	KeyObjFactory.setSecret(secret);
	KeyObjFactory.setRandomSeed(seed);
	KeyObjFactory.genIV();
	key = KeyObjFactory.getKeyObj(clientid,firmid);

	KeyObjFactory.setRandomSeed(seed);
	KeyObjFactory.genIV();
	key2 = KeyObjFactory.getKeyObj(clientid,firmid);
	Assert.assertArrayEquals(key.getKey(),key2.getKey());
    }

    /* 
     * Opposite of test above, this test confirms that if we change the seed
     * that the generated keys will always be different.
     */

    public void testDiffKeySeed()
    {
        // MjE0NTc2NDM=/MTIzNDU2Nw== 
        
        byte[] clientid = Base64.decodeBase64("MjE0NTc2NDM=");
	
        byte[] firmid = Base64.decodeBase64("MTIzNDU2Nw==");
	byte[] secret = Base64.decodeBase64("aSBsb3ZlIGplbiEh");
	byte[] seed = new byte[200];
	ThreadedSeedGenerator gen = new ThreadedSeedGenerator();
	seed = gen.generateSeed(200,false);

        KeyObj key,key2;
	KeyObjFactory.setSecret(secret);
	KeyObjFactory.setRandomSeed(seed);
	KeyObjFactory.genIV();
	key = KeyObjFactory.getKeyObj(clientid,firmid);
	seed = gen.generateSeed(200,false);
	KeyObjFactory.setRandomSeed(seed);
	KeyObjFactory.genIV();
	key2 = KeyObjFactory.getKeyObj(clientid,firmid);
	Assert.assertThat(key.getKey(),IsNot.not(IsEqual.equalTo(key2.getKey())));
    }

    /* 
     * Last key sanity check; this test confirms that if we change the
     * secret only the generated keys will be different.
     */

    public void testDiffKeySecret()
    {
        // MjE0NTc2NDM=/MTIzNDU2Nw== 
        
        byte[] clientid = Base64.decodeBase64("MjE0NTc2NDM=");
	
        byte[] firmid = Base64.decodeBase64("MTIzNDU2Nw==");
	byte[] secret = Base64.decodeBase64("aSBsb3ZlIGplbiEh");
	byte[] secret2 = Base64.decodeBase64("amVuYmFieSBzbGVlcGluZyEh");
	byte[] seed = new byte[200];
	ThreadedSeedGenerator gen = new ThreadedSeedGenerator();
	seed = gen.generateSeed(200,false);

        KeyObj key,key2;
	KeyObjFactory.setSecret(secret);
	KeyObjFactory.setRandomSeed(seed);
	KeyObjFactory.genIV();
	key = KeyObjFactory.getKeyObj(clientid,firmid);
	KeyObjFactory.setSecret(secret2);
	key2 = KeyObjFactory.getKeyObj(clientid,firmid);
	Assert.assertThat(key.getKey(),IsNot.not(IsEqual.equalTo(key2.getKey())));
    }
}

