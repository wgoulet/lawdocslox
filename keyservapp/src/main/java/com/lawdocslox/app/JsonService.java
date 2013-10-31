package com.lawdocslox.app;

// Full credit to http://www.jeenisoftware.com/spring-3-mvc-json-example/
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.context.annotation.CommonAnnotationBeanPostProcessor;
import org.springframework.context.annotation.PropertySource;
import org.springframework.context.support.PropertySourcesPlaceholderConfigurer;
import org.springframework.beans.factory.annotation.*;
import org.springframework.core.env.*;
import org.apache.log4j.ConsoleAppender;
import org.apache.log4j.Logger;
import org.apache.log4j.*;
import java.util.Properties;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.File;

import javax.annotation.PostConstruct;

import java.util.HashMap;
import java.util.Map;
import org.apache.commons.codec.binary.Base64;

@Controller
public class JsonService {
  private static Logger log = Logger.getLogger(JsonService.class); 


  private static Map<String, Person> data = new HashMap<String, Person>();
  static{
    data.put("ADAM", new Person("Adam", "Davies", 42));
    data.put("JANE", new Person("Jane", "Harrison", 35));
    data.put("RAGNAR", new Person("RAGNAR", "GOULET", 2));
    data.put("ANGUS", new Person("Angus", "FUNG", 37));
    data.put("DOMINIQUE", new Person("DOMINQUE", "GOULET", 1));
    data.put("HELLO", new Person("Hello", "ICAN", 1));
    data.put("docs", new Person("docs", "cool", 2));
    data.put("github", new Person("rocks", "man!", 3));
            
  }

  @Value ("#{myProps['keyfile']}")
  private String keyfile;

  @Value("#{myProps['seedsize']}")
  private int seedsize;

  @Value("#{myProps['initsecret']}")
  private String initsecret;

  private String seed;
  private String secret;
  private String iv;

  @PostConstruct
  public void init()
  {
	// Look for secret and seed values to initialize KeyObjFactory
	// with. If they don't exist, create new ones and store in 
	// properties file
	Properties props = new Properties();
	File keys = new File(keyfile);
	if(!keys.exists())
	{
		try
		{
			keys.createNewFile();
		}catch(Exception e)
		{
			e.printStackTrace();
			System.exit(1);
		}
	}
	  try
	  {
	  	FileInputStream fstream = new FileInputStream(keyfile);
		
		props.load(fstream);
		if((props.containsKey("seed") 
		&&(props.containsKey("secret")  
		&&(props.containsKey("iv")))))
		{
			seed = props.getProperty("seed");
			secret = props.getProperty("secret");
			iv = props.getProperty("iv");
			KeyObjFactory.setRandomSeed(Base64.decodeBase64(seed));
			KeyObjFactory.setSecret(Base64.decodeBase64(secret));
			KeyObjFactory.setIV(Base64.decodeBase64(iv));
		}
		else
		{
			byte[] seedbytes = new byte[seedsize];
			byte[] ivbytes = new byte[seedsize];
			seedbytes = KeyObjFactory.genRandVal(seedsize);
			props.setProperty("seed",Base64.encodeBase64(seedbytes).toString());
			props.setProperty("secret", initsecret);
			seed = props.getProperty("seed");
			secret = props.getProperty("secret");
			KeyObjFactory.setRandomSeed(Base64.decodeBase64(seed));
			KeyObjFactory.setSecret(Base64.decodeBase64(secret));
			KeyObjFactory.genIV();
			int ivsize = KeyObjFactory.getIV(ivbytes, seedsize);
			props.setProperty("iv", Base64.encodeBase64(ivbytes).toString());
	  		try
			{
				FileOutputStream fostream = new FileOutputStream(keyfile);
				props.store(fostream, "");
			}catch (Exception e)
	  		{
				  e.printStackTrace();
				  System.exit(1);
			}
		}
	  }catch(Exception e)
	  {
		  e.printStackTrace();
		  System.exit(1);
	  }

	log.info("Initialized KeyObjFactory");
  }
  
  @RequestMapping(value="/key/{clientid}/{firmid}")
  public @ResponseBody KeyObj getKey(@PathVariable String clientid,@PathVariable String firmid){
	  int len = Base64.decodeBase64(clientid).length;
	  int len2 = Base64.decodeBase64(firmid).length;
          byte cliarr[] = new byte[len];
	  byte firmarr[] = new byte[len2];
          cliarr = Base64.decodeBase64(clientid);
          firmarr = Base64.decodeBase64(firmid);
	  KeyObj key = KeyObjFactory.getKeyObj(cliarr, firmarr);
	  return key;
  }
  
  @RequestMapping(value="{name}", method = RequestMethod.GET)
  public @ResponseBody Person getPerson(@PathVariable String name){
    Person p = data.get(name.toUpperCase());
	  log.info("getting data");
    return p;
  }
}
