

import java.util.*;

public class SimulateGame {
   

    private static Player playerOne = new Player("Bob");
    private static Player playerTwo = new Player("Alice");
    private static Player currentPlayer ;
    private static ArrayList<Player> playersList = new ArrayList<Player>();
    private static Deck deck = new Deck(true); // Shuffle deck automatically
    private static ArrayList<Card> table = new ArrayList<>();
    private static Card topCard;
    private static int roundsPlayed = 1;
    private static boolean gameOver = false;

    

    public static void main(String[] args) {
        
        playersList.add(playerOne);
        playersList.add(playerTwo);
        playersList.add(new Player("mannooubi"));
        playersList.add(new Player("lotfi"));
        currentPlayer = playersList.get(0);

        playGame();
    }

    // Methods

    // Play the simple card game
    public static void playGame() {
        System.out.println("Starting simple card game simulation...");
        System.out.println();

        dealCards(); // Deal 26 cards to each player
        chooseFirstPlayer(); // Choose who goes first
        playRounds(); // Start the rounds
        declareWinner(); // Declare a winner
    }

    // Deal 26 cards to each hand in alternating order
    public static void dealCards() {
        for (int j=0;j<playersList.size();j++){
            for (int i = 0; i < 13; i++) {
                playersList.get(j).takeCard(deck.deal());
               
            }
        }
      
    }

    // Choose who goes first
    public static void chooseFirstPlayer() {
        Random random = new Random();
        int n = random.nextInt(4);

        if (n == 1) { // Make playerTwo the new playerOne
            Player temp = playerOne;
            playerOne = playerTwo;
            playerTwo = temp;
        }
    }

    // Play rounds, max 10
    public static void playRounds() {
        while (roundsPlayed <= 10 && (gameOver == false)) {
            // Display the round number
            System.out.println("ROUND " + roundsPlayed);
            System.out.println();

            // Display each player's hand
            displayHands();

            // Play individual round
            playRound();

            // Increment roundsPlayed counter
            roundsPlayed++;    
        }
    }

    // Play an individual round
    public static void playRound() {
        boolean suitMatch = false; // Flag for notifying a suit match
        Card cardToPlay;
        for(int i=0;i<playersList.size();i++){
            if (playersList.get(i).handSize() == 20)  {
                gameOver = true;
            }
        }
       

        while (suitMatch == false) {
            // Current player places card on table
            cardToPlay = currentPlayer.playCard();
            table.add(cardToPlay);

            // Check if there's a suit match
            suitMatch = checkSuitMatch();

            if (suitMatch == false)
                switchCurrentPlayer();
        }

        collectCards();
        System.out.println();

        // Sleep for a second before beginning a new round
        try {
            Thread.sleep(500);
        }
        catch (InterruptedException e) {
        }
    }

    // Switch current player
    public static void switchCurrentPlayer() {
        if (currentPlayer == playersList.get(0)){
            currentPlayer = playersList.get(1);
        }else if(currentPlayer == playersList.get(1)){
            currentPlayer = playersList.get(2);
        }else if(currentPlayer == playersList.get(2)){
            currentPlayer = playersList.get(3);
        }
        else if (currentPlayer == playersList.get(3)){
            currentPlayer = playersList.get(0);
        }
            
    }

    // Check for a suit match
    public static boolean checkSuitMatch() {
        int tableSize = table.size();
        int lastSuit;
        int topSuit;
        if (tableSize < 2) {
            return false;
        }
        else {
            lastSuit = table.get(tableSize - 1).getSuit();
            topSuit = table.get(tableSize - 2).getSuit();
        }

        // Check suit equivalence
        if (lastSuit == topSuit) {
            System.out.println();
            System.out.println(currentPlayer.getName() + " wins the round!");
            System.out.println();

            return true;
        }

        return false;
    }

    // Collect cards from table
    public static void collectCards() {
        // Print a message
        System.out.print(currentPlayer.getName() + " takes the table (" +
            table.size() + "): ");
        displayTable();

        // Player takes each card from the table and adds to hand
        for (int i = 0; i < table.size(); i++) {
            Card cardToTake = table.get(i);
            currentPlayer.takeCard(cardToTake);
        }

        table.clear();
    }

    // Displays all the cards currently on the table
    public static void displayTable() {
        for (int i = 0; i < table.size(); i++) {
            if (table.get(i) != null) {
                System.out.print(table.get(i).getName() + " ");
            }
        }

        System.out.println();
        System.out.println();
    }

    // Displays each player's current hand
    public static void displayHands() {
        for(int i=0;i<playersList.size();i++){
            playersList.get(i).displayHand();
        }
    }

    // Declare a winner
    public static void declareWinner() {
        Player tmp = playersList.get(0);
        for(int i =0;i<playersList.size();i++ ){
            if(playersList.get(i).handSize() == 0){
                System.out.println(tmp.getName().toUpperCase() + " WINS " +  "WITH A TOTAL OF " + playersList.get(i).handSize() + " CARDS!");
            }
        }
        
            
       

        System.out.println();
    }
}