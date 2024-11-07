import networkx as nx
import community as community_louvain
from collections import defaultdict

WORD_DICT = 'words_12dict.csv'

def main():
    
    wordLength = int(input("Desired Word Length: "))

    #get all the words for the given wordlength
    words = read_file(wordLength)

    #find each pair connection
    allPairs, connectedWords = find_pairs(wordLength, words)

    # get the most used words
    mostUsedWords = find_max(allPairs)

    #create the network graph
    Graph = create_graph(connectedWords, allPairs, mostUsedWords[0])

    # #find the longest transformation chain
    find_diameter(Graph)

    # #find the groupings for the dataset
    find_community(Graph)

    # #find the most centralized nodes
    find_betweenness_centrality(Graph)

    #export for visual graphs
    export_to_DOT(words, allPairs, wordLength)



def read_file(wordLength):
    #open the dictionary file and read its contents
    with open(WORD_DICT, 'r') as file:
        data = file.read()
        data = data.split("\n")

        #find just the length of word that we need and make them uppercase
        words = [word.upper() for word in data[wordLength - 1].split(",")]

    print(f"\nLoaded {len(words)} {wordLength} letter words")
    return words

def find_pairs(wordLength, words):

    connectedWords = set()
    pairChecker    = set()

    #generate all possible 1 letter byte differences
    for i in range(wordLength):
        for j in range(32):
            group = i * 8
            pairChecker.add(j << group)

    
    allPairs = []
    #grab each word to compare
    for i in range(len(words)):
        origNumWord = words[i]
        
        #compare with each other word
        for j in range(i):
            comparisonNumWord = words[j]
            #if the two words are a letter off
            if (convert_word_to_number(origNumWord) ^ convert_word_to_number(comparisonNumWord)) in pairChecker:
                #add the words to our pairs
                allPairs.append((origNumWord, comparisonNumWord))
                connectedWords.add(origNumWord)
                connectedWords.add(comparisonNumWord)
    print(f"There are {len(allPairs)} connections in the {wordLength} letter words\n")
    return allPairs, connectedWords

#Converts words to a unique number to compare
def convert_word_to_number(word):
    uniqueNumber = 0
    multiplier = 1
    #convert each character to a unique value
    for character in word:
        uniqueNumber += (ord(character) - ord('A')) * multiplier
        #multiply by and extra 256 to get us to the next byte
        multiplier *= 256
    return uniqueNumber
    
def find_max(allPairs):
    wordCounter = {}

    # Count occurrences of each word in the pairs
    for word1, word2 in allPairs:
        wordCounter[word1] = wordCounter.get(word1, 0) + 1
        wordCounter[word2] = wordCounter.get(word2, 0) + 1

    # Sort words by frequency in descending order and get the top 10
    topWords = sorted(wordCounter.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Extract just the words from the top items
    mostUsedWords = [word for word, count in topWords]
    
    print(f"{mostUsedWords[0]} is the most used word with {wordCounter[mostUsedWords[0]]} connections")
    print(f"Top 10 most connected words: {mostUsedWords}")
    return mostUsedWords

def create_graph(connectedWords, allPairs, maxWord):
    Graph = nx.Graph()

    #create a node for each word
    for word in connectedWords:
        Graph.add_node(word)

    #create an edge for each word and track how many edges each word has
    for i in range(len(allPairs)):
        Graph.add_edge(allPairs[i][0], allPairs[i][1])
    
    #remove each word that doesnt connect to the main graph
    #this will keep the graph continous for diameter
    for word in connectedWords:
        if(not nx.has_path(Graph, word, maxWord)):
            Graph.remove_node(word)

    return Graph

def find_betweenness_centrality(Graph):
    #calculate centrality
    betweenness = nx.betweenness_centrality(Graph)

    #show the most central items
    print("\nCentralized Words : ")
    for node, centrality in sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"{node}: {centrality}")



def find_community(Graph):
    partition = community_louvain.best_partition(Graph)

    communities = defaultdict(list)
    for node, community in partition.items():
        communities[community].append(node)

    print("Communities : ")
    # Print the first few words from each community
    for community, words in communities.items():
        print(f"Community {community}: {', '.join(words[:5])}")


def find_diameter(Graph):
    shortest_path_lengths = dict(nx.all_pairs_shortest_path_length(Graph))

    # Identify the pair of nodes with the longest shortest path (diameter)
    max_distance = 0
    diameter_nodes = None

    #compute the distance for each
    for node1, paths in shortest_path_lengths.items():
        for node2, distance in paths.items():
            if distance > max_distance:
                max_distance = distance
                diameter_nodes = (node1, node2)

    # Retrieve the path for the diameter
    if diameter_nodes:
        diameter_path = nx.shortest_path(Graph, source=diameter_nodes[0], target=diameter_nodes[1])
        print(f"\nThe diameter is {max_distance} steps long.")
        print("Words in the diameter path:", diameter_path, "\n")

def export_to_DOT(words, allPairs, wordLength):
    #Use the avaialable words and pairs to generate a DOT file for exporting
    with open(f"wordLadder.dot",'w') as file:
        file.write('graph words {\n')
        #Add each word as a node
        for word in words:
            file.write('  "' + word + '";\n')
        #Add each pair as an edge
        for pair1,pair2 in allPairs:
            file.write('  "' + pair1 + '" -- "' + pair2 + '";\n')
        file.write('}\n')







main()