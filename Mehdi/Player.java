import java.util.Random;
import java.util.Scanner;


public class Player {
     // Attributes

     private Hand hand;
     private String name;
     
     Scanner sc = new Scanner(System.in);
     // Default constructor

     public Player(String name) {
          hand = new Hand(); // Instantiate new hand object
          this.name = name;
	  
     }

     // Methods

     public Card playCard() {
          System.out.println("chose which card to play ");
          int i = sc.nextInt();
          Card c = hand.playCard(i);
          System.out.println(String.format("%5s", name) + " plays a " + c.getName() + "!");

          return c;
     }

     public void takeCard(Card card) {
          hand.addCard(card);
     }

     public String getName() {
          return name;
     }
     
     public void displayHand() {
          System.out.println(name + "\'s hand (" + hand.getSize() + "):");
          hand.display();
          System.out.println();
     }

     public int handSize() {
          return hand.getSize();
     }
}
