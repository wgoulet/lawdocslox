package com.lawdocslox.app;
import java.lang.System;
import com.lawdocslox.app.KeyObj;
import org.bouncycastle.crypto.generators.*;
import org.bouncycastle.crypto.digests.*;
import org.bouncycastle.crypto.examples.DESExample;
import org.bouncycastle.crypto.params.KDFParameters;
import org.bouncycastle.crypto.prng.DigestRandomGenerator;

class KeyObjFactory {
    private static byte[] secret;
    private static byte[] iv;
    private static byte[] seed;
    public static void setSecret(byte[] in) 
    {
	    secret = new byte[in.length];
	    System.arraycopy(in, 0, secret, 0, in.length);
    }
    public static void genIV()
    {
	    iv = new byte[200];
	    SHA256Digest d = new SHA256Digest();
	    d.update(seed, 0, seed.length);
	    DigestRandomGenerator dr = new DigestRandomGenerator(d);
	    dr.nextBytes(iv);
    }
    public static void setRandomSeed(byte[] in)
    {
	    seed = new byte[in.length];
	    System.arraycopy(in,0,seed,0,in.length);
    }
    public static KeyObj getKeyObj(byte[] clientid,byte[] firmid) {
	/* Key generation algorithm is as follows:
	 * 1) Get a shared secret based on input from static config file
	 * 2) Generate an IV with a PRNG. Will use DigestRandomGenerator
	 * that will be calculated across init data passed in by calling
	 * class. PRNG will be seeded using provided threadedSeedGenerator.
	 * 3) Build KDFparams using IV and shared secret and pass to 
	 * KDF2BytesGenerator .
	 */


	SHA256Digest d = new SHA256Digest();
	d.update(clientid, 0, clientid.length);
	d.update(firmid,0,firmid.length);
	//byte[] seed = new byte[d.getDigestSize()];	
	d.finish();
	//d.doFinal(seed, 0);
	KDF2BytesGenerator kg = new KDF2BytesGenerator(d);
	KDFParameters kp = new KDFParameters(iv,secret);
	kg.init(kp);
	byte[] keyval = new byte[200];
	
	kg.generateBytes(keyval, 0, keyval.length);

        return new KeyObj(keyval,10);
    }
}
