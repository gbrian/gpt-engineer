import java.util.*;
import java.io.*;

public class DummyJava {
    public String publicProperty;
    private int privateProperty;

    public DummyJava(String publicProperty, int privateProperty) {
        this.publicProperty = publicProperty;
        this.privateProperty = privateProperty;
    }

    public void publicMethodNoParams() {
        System.out.println("This is a public method with no parameters.");
    }

    private void privateMethodMultipleParams(String param1, int param2) {
        System.out.println("This is a private method with multiple parameters: " + param1 + ", " + param2);
    }

    public void dummyMethod() {}
}