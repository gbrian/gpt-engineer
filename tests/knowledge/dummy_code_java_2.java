package com.fake.package;

import java.util.Random;
import java.util.List;
import java.util.ArrayList;

// class decorator
public class MyClass {

    // 3 Class Properties
    private int firstProperty;
    private String secondProperty;
    private List<Double> thirdProperty;

    // Default Constructor
    public MyClass() {
        thirdProperty = new ArrayList<>();
        secondProperty = "Hello World";
        firstProperty = 0;
    }

    // 10 Methods
    public int getFirstProperty() {
        return firstProperty;
    }

    public void setFirstProperty(int firstProperty) {
        this.firstProperty = firstProperty;
    }

    public String getSecondProperty() {
        return secondProperty;
    }

    public void setSecondProperty(String secondProperty) {
        this.secondProperty = secondProperty;
    }

    public List<Double> getThirdProperty() {
        return thirdProperty;
    }

    public void setThirdProperty(List<Double> thirdProperty) {
        this.thirdProperty = thirdProperty;
    }

    public void addElementToThirdProperty(Double element) {
        thirdProperty.add(element);
    }

    public Double getRandomElementFromThirdProperty() {
        Random rand = new Random();
        return thirdProperty.get(rand.nextInt(thirdProperty.size()));
    }

    public void removeElementFromThirdProperty(Double element) {
        thirdProperty.remove(element);
    }

    public void clearThirdProperty() {
        thirdProperty.clear();
    }

    // 2 Static Methods
    public static void printHelloWorld() {
        System.out.println("Hello World from static method");
    }

    public static int addTwoIntegers(int a, int b) {
        return a + b;
    }
}
