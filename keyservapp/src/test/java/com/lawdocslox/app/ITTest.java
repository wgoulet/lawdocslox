/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package com.lawdocslox.app;
//import static org.hamcrest.Matchers.containsString;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.forwardedUrl;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.handler;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.ContextHierarchy;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.test.context.web.WebAppConfiguration;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;
import org.springframework.web.servlet.resource.DefaultServletHttpRequestHandler;

/**
 * Tests dependent on access to resources under the web application root directory.
 *
 * @author Rossen Stoyanchev
 */
@RunWith(SpringJUnit4ClassRunner.class)
@WebAppConfiguration("src/test/resources/META-INF/web-resources")
@ContextHierarchy({
        @ContextConfiguration("root-context.xml"),
        @ContextConfiguration("servlet-context.xml")
})
public class ITTest {

        @Autowired
        private WebApplicationContext wac;

        private MockMvc mockMvc;

        @Before
        public void setup() {
                this.mockMvc = MockMvcBuilders.webAppContextSetup(this.wac).alwaysExpect(status().isOk()).build();
        }
        
        @Test
        public void testgetkey() throws Exception {
                this.mockMvc.perform(get("/keyserv/key/MjE0NTc2NDM=/MTIzNDU2Nw==")).andReturn();
                        //.andExpect(forwardedUrl("/WEB-INF/layouts/standardLayout.jsp"));
        }
}