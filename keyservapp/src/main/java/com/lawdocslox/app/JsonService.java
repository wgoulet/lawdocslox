package com.lawdocslox.app;

// Full credit to http://www.jeenisoftware.com/spring-3-mvc-json-example/
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.HashMap;
import java.util.Map;
import org.apache.commons.codec.binary.Base64;

@Controller
public class JsonService {

  private static Map<String, Person> data = new HashMap<String, Person>();
  static{
    data.put("ADAM", new Person("Adam", "Davies", 42));
    data.put("JANE", new Person("Jane", "Harrison", 35));
    data.put("RAGNAR", new Person("RAGNAR", "GOULET", 2));
  }
  
  @RequestMapping(value="/key/{clientid}/{firmid}")
  public @ResponseBody KeyObj getKey(@PathVariable String clientid,@PathVariable String firmid){
	  //TODO: Horribly insecure and hacky. Need to check proper limit
          //of input params and set size of cliarr/firmarr based on that size
      
          byte cliarr[] = new byte[20];
	  byte firmarr[] = new byte[20];
          cliarr = Base64.decodeBase64(clientid);
          firmarr = Base64.decodeBase64(firmid);
	  KeyObj key = KeyObjFactory.getKeyObj(cliarr, firmarr);
	  return key;
  }
  
  @RequestMapping(value="{name}", method = RequestMethod.GET)
  public @ResponseBody Person getPerson(@PathVariable String name){
    Person p = data.get(name.toUpperCase());
    return p;
  }
}
