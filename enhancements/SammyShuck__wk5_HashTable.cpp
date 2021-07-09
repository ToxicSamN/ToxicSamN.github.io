//============================================================================
// Name        : HashTable.cpp
// Author      : Sammy Shuck
// Course      : CS260-J5450 Data Structures and Algorithms
// Project     : Week5 Lab 5-2
// Date        : 06/07/2020
// Version     : 1.0
// Copyright   : Copyright © 2017 SNHU COCE
// Description : Lab 5-2 Hash Tables and Chaining
//============================================================================

#include <algorithm>
#include <climits>
#include <iostream>
#include <string> // atoi
#include <time.h>
#include <array>
#include <vector>

#include "CSVparser.hpp"

using namespace std;

//============================================================================
// Global definitions visible to all methods and classes
//============================================================================

const unsigned int DEFAULT_SIZE = 179;

// forward declarations
double strToDouble(string str, char ch);


// define a structure to hold bid information
struct Bid {
    string bidId; // unique identifier
    string title;
    string fund;
    double amount;
    Bid() {
        amount = 0.0;
    }
};

// forward declarations
void displayBid(const Bid& bid);

//============================================================================
// Hash Table class definition
//============================================================================

/**
 * Define a class containing data members and methods to
 * implement a hash table with chaining.
 */
class HashTable {

private:

    // define a structure to hold bid information
    struct Node {
        Bid bid;
        Node* next;
        // init value for checking if struct
        // has been initialized
        bool init;

        // default Node constructor
        Node() {
            next = nullptr;
            init = false;
        }

        // constructor with a bid
        // calls the default constructor
        Node(Bid b) : Node() {
            bid = b;
            init = true;
        }
    };

    unsigned int tableSize = DEFAULT_SIZE;
    // use a pointer array for storing the nodes
    // and initialize with DEFAULT_SIZE
    vector<Node> nodes;

    unsigned int hash(int key);

public:
    HashTable();
    HashTable(unsigned int size_t);
    virtual ~HashTable();
    void Insert(Bid bid);
    void PrintAll();
    void Remove(string bidId);
    Bid Search(string bidId);
    void Resize(unsigned int size_t);
    unsigned int Size();
};

/**
 * Default constructor
 */
HashTable::HashTable() {

    // set the nodes vector size to default table size
    nodes.resize(tableSize);
}
/**
 * Constructor with custom table size
 */
HashTable::HashTable(unsigned int size_t) {
    // set the nodes vector size to provided size
    nodes.resize(size_t);
    // store table size into object
    tableSize = size_t;
}

/**
 * Destructor
 */
HashTable::~HashTable() {

    // using vector method erase to free up memory
    nodes.erase(nodes.begin());
}

/**
 * Calculate the hash value of a given key.
 * Note that key is specifically defined as
 * unsigned int to prevent undefined results
 * of a negative list index.
 *
 * @param key The key to hash
 * @return The calculated hash
 */
unsigned int HashTable::hash(int key) {

    unsigned mod = key % tableSize;
    return mod;
}

/**
 * Insert a bid
 *
 * @param bid The bid to insert
 */
void HashTable::Insert(Bid bid) {

    // convert bidId to ascii and convert that to int using atoi
    //  call hash method to return the hash value for the bid
    unsigned key = hash(atoi(bid.bidId.c_str()));
    // call node constructor with bid struct
    Node* n = new Node(bid);

    // does a node already exist at array index
    if (nodes[key].init) {
        // already a bid at index, construct a chain
        // get the first node in the list
        Node* exstNode = &nodes[key];

        // find the end of the linked list
        while (exstNode->next != nullptr) {
            exstNode = exstNode->next;
        }
        // assign the last element in the linked list as the new node
        exstNode->next = n;
    }else {
        // no bid at index , so add one
        nodes[key] = *n;
    }
}

/**
 * Print all bids
 */
void HashTable::PrintAll() {

    // loop through the entire array to print out the
    // bids stored in the hash table
    for (int i = 0; i<tableSize; ++i) {
        // only print out elements of real data
        if (nodes[i].init) {
            // ensure we are following any linked list
            Node* exstNode = &nodes[i];

            // loop until end of linked list
            bool firstLoop = true;
            while (exstNode != nullptr) {
                // per formatting requirements formulate the output
                if (firstLoop){ cout<<"Key "; firstLoop= false; }
                else { cout<<"    "; }

                cout<<i<<": ";
                // display the Bid
                displayBid(exstNode->bid);
                // assign the next node to exstNode
                exstNode = exstNode->next;
            }
        }
    }
}

/**
 * Remove a bid
 *
 * @param bidId The bid id to search for
 */
void HashTable::Remove(string bidId) {

    // convert bidId to ascii and convert that to int using atoi
    //  call hash method to return the hash value for the bid
    unsigned key = hash(atoi(bidId.c_str()));

    // does a node already exist at array index
    if (nodes[key].init) {
        // a bid exists at array index
        // verify the requested bidId can be found at index

        // define a current node tracker
        Node* currNode = &nodes[key];
        // need to track the previous node of a linked list
        Node* prevNode = &nodes[key];

        // traverse the linked list
        while (currNode != nullptr) {
            if (currNode->bid.bidId == bidId){
                // found it!
                // remove the bid from the list

                // check if found bid is not beginning node
                if (prevNode != currNode) {
                    prevNode->next = currNode->next;
                    delete currNode;
                    // break out of the loop
                    break;
                }
                // bid not in middle so it is at the beginning
                else {
                    // if next node is null then null array element at index
                    if (currNode->next == nullptr){
                        // delete the node
                        delete currNode;
                    }
                    // otherwise set the next node as the array index value
                    else{
                        nodes[key] = *currNode->next;
                    }
                }

            }
            // set prev node to currNode
            prevNode = currNode;
            // set currNode to next
            currNode = currNode->next;
        }

    }
}

/**
 * Search for the specified bidId
 *
 * @param bidId The bid id to search for
 */
Bid HashTable::Search(string bidId) {
    Bid bid;

    // convert bidId to ascii and convert that to int using atoi
    //  call hash method to return the hash value for the bid
    unsigned key = hash(atoi(bidId.c_str()));

    // does a node already exist at array index
    if (nodes[key].init) {
        // a bid exists at array index
        // verify the requested bidId can be found at index

        // define a current node tracker
        Node* currNode = &nodes[key];

        // traverse the linked list
        while (currNode != nullptr) {
            if (currNode->bid.bidId == bidId) {
                // found it!
                // return the bid from the list
                return currNode->bid;
            }
            // set currNode to next
            currNode = currNode->next;
        }

    }

    return bid;
}

void HashTable::Resize(unsigned int size_t){
    nodes.resize(size_t);
    tableSize = size_t;
}

unsigned int HashTable::Size(){
    return nodes.size();
}

//============================================================================
// Static methods used for testing
//============================================================================

/**
 * Display the bid information to the console (std::out)
 *
 * @param bid struct containing the bid info
 */
void displayBid(const Bid& bid) {
    cout << bid.bidId << ": " << bid.title << " | " << bid.amount << " | "
            << bid.fund << endl;
    return;
}

/**
 * Load a CSV file containing bids into a container
 *
 * @param csvPath the path to the CSV file to load
 * @return a container holding all the bids read
 */
void loadBids(string csvPath, HashTable* hashTable) {
    cout << "Loading CSV file " << csvPath << endl;

    // Define a vector data structure to hold a collection of bids.
    vector<Bid> bids;

    // initialize the CSV Parser using the given path
    csv::Parser file = csv::Parser(csvPath);
    hashTable->Resize(file.rowCount());
    unsigned int i;

    try {
        // loop to read rows of a CSV file
        for (i = 0; i < file.rowCount(); i++) {

            // Create a data structure and add to the collection of bids
            Bid bid;
            bid.bidId = file[i][1];
            bid.title = file[i][0];
            bid.fund = file[i][8];
            bid.amount = strToDouble(file[i][4], '$');

            //cout << "Item: " << bid.title << ", Fund: " << bid.fund << ", Amount: " << bid.amount << endl;

            // push this bid to the end
            hashTable->Insert(bid);
        }
    } catch (csv::Error &e) {
        std::cerr << e.what() << std::endl;
    }
}

/**
 * Simple C function to convert a string to a double
 * after stripping out unwanted char
 *
 * credit: http://stackoverflow.com/a/24875936
 *
 * @param ch The character to strip out
 */
double strToDouble(string str, char ch) {
    str.erase(remove(str.begin(), str.end(), ch), str.end());
    return atof(str.c_str());
}

/**
 * The one and only main() method
 */
int main(int argc, char* argv[]) {

    // process command line arguments
    string csvPath, bidKey;
    switch (argc) {
    case 2:
        csvPath = argv[1];
        bidKey = "98109";
        break;
    case 3:
        csvPath = argv[1];
        bidKey = argv[2];
        break;
    default:
        //csvPath = "eBid_Monthly_Sales.csv";
        csvPath = "eBid_Monthly_Sales_Dec_2016.csv";
        //bidKey = "98288";
        bidKey = "98109";
    }

    // Define a timer variable
    clock_t ticks;

    // Define a hash table to hold all the bids
    HashTable* bidTable;

    Bid bid;

    int choice = 0;
    while (choice != 9) {
        cout << "Menu:" << endl;
        cout << "  1. Load Bids" << endl;
        cout << "  2. Display All Bids" << endl;
        cout << "  3. Find Bid" << endl;
        cout << "  4. Remove Bid" << endl;
        cout << "  9. Exit" << endl;
        cout << "Enter choice: ";
        cin >> choice;

        switch (choice) {

        case 1:
            bidTable = new HashTable();

            // Initialize a timer variable before loading bids
            ticks = clock();

            // Complete the method call to load the bids
            loadBids(csvPath, bidTable);
            cout<<bidTable->Size()<<" bids read"<<endl;

            // Calculate elapsed time and display result
            ticks = clock() - ticks; // current clock ticks minus starting clock ticks
            cout << "time: " << ticks << " clock ticks" << endl;
            cout << "time: " << ticks * 1.0 / CLOCKS_PER_SEC << " seconds" << endl;
            break;

        case 2:
            bidTable->PrintAll();
            break;

        case 3:
            ticks = clock();

            bid = bidTable->Search(bidKey);

            ticks = clock() - ticks; // current clock ticks minus starting clock ticks

            if (!bid.bidId.empty()) {
                displayBid(bid);
            } else {
                cout << "Bid Id " << bidKey << " not found." << endl;
            }

            cout << "time: " << ticks << " clock ticks" << endl;
            cout << "time: " << ticks * 1.0 / CLOCKS_PER_SEC << " seconds" << endl;
            break;

        case 4:
            bidTable->Remove(bidKey);
            break;
        }
    }

    cout << "Good bye." << endl;

    return 0;
}
