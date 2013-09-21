package com.lawdocslox.app;
import org.restlet.*;
import org.restlet.data.*;
import org.restlet.resource.ServerResource;
import org.restlet.resource.*;

public class App extends ServerResource {  

   public static void main(String[] args) throws Exception {  
      // Create the HTTP server and listen on port 8182  
      new Server(Protocol.HTTP, 8182, App.class).start();  
   }

   @Get  
   public String toString() {  
      return "i love jen!!";  
   }

}  
