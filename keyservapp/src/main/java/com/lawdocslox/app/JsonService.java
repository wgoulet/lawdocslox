package com.lawdocslox.app;

// Full credit to http://www.jeenisoftware.com/spring-3-mvc-json-example/
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.HashMap;
import java.util.Map;

@Controller
public class JsonService {

  private static Map<String, Person> data = new HashMap<String, Person>();
  static{
    data.put("ADAM", new Person("Adam", "Davies", 42));
    data.put("JANE", new Person("Jane", "Harrison", 35));
    data.put("RAGNAR", new Person("RAGNAR", "GOULET", 2));
  }

  @RequestMapping(value="{name}", method = RequestMethod.GET)
  public @ResponseBody Person getPerson(@PathVariable String name){
    Person p = data.get(name.toUpperCase());
    return p;
  }
}
