from WordTrie import WordTrie

def findWords(board: list, wordTrie, currentPoint: tuple, foundWords: list = None, workingStrand: tuple = None):
    if foundWords is None:
        foundWords = []
    if workingStrand is None:
        workingStrand = ("", [])  # (current string, list of coordinates)
    
    row, col = currentPoint
    letter = board[row][col]
    # Mark the board as visited
    board[row][col] = None
    
    # Append the current letter and point to the working strand
    current_str, path = workingStrand
    current_str += letter
    path = path + [currentPoint]  # create a new list so each branch is independent
    
    # If the current string is a complete word, add it to the found words.
    wordTrieSearch = wordTrie.search(current_str)
    if wordTrieSearch[0]:
        foundWords.append((current_str, path))
    
    # Get feasible next letters from the trie based on the current prefix.
    feasibleNextLetters = set(wordTrieSearch[1])
    
    # All possible directions (8-connected neighbors)
    directions = [(row+1, col), (row-1, col), (row, col+1), (row, col-1),
                  (row+1, col+1), (row-1, col-1), (row+1, col-1), (row-1, col+1)]
    
    # Explore all valid moves that are feasible according to the trie.
    for newX, newY in directions:
        if 0 <= newX < len(board) and 0 <= newY < len(board[0]) and board[newX][newY] is not None:
            if board[newX][newY] in feasibleNextLetters:
                findWords(board, wordTrie, (newX, newY), foundWords, (current_str, path))
    
    # Backtracking: restore the current board cell.
    board[row][col] = letter
    return foundWords
def validatePuzzle(board: list, wordTrie, importantWords: list):
    allWords = []
    for row in range(len(board)):
        for col in range(len(board[0])):
            allWords.append(findWords(board, wordTrie, (row, col)))
    allWordsJoined = []
    for sublist in allWords:
        allWordsJoined += sublist

    print("All important words found:", [word for word in allWordsJoined if word[0] in importantWords])

    valid = True
    wordCoordSet = {}
    for word in allWordsJoined:
        if word[0] not in importantWords:
            continue
        try:
            if wordCoordSet[word[0]] != set(word[1]):
                print("This word was found in multiple locations:")
                print(word[0])
                valid = False
        except:
            wordCoordSet[word[0]] = set(word[1])
    for word in importantWords:
        if word not in [words[0] for words in allWordsJoined]:
            print("This word was not found:")
            print(word)
            valid = False
    return valid
def calculateSetOfWords(board: list, wordTrie):
    allWords = []
    for row in range(len(board)):
        for col in range(len(board[0])):
            allWords.append(findWords(board, wordTrie, (row, col)))
    allWordsJoined = []
    for sublist in allWords:
        allWordsJoined += sublist
    return set([word[0] for word in allWordsJoined])


if __name__ == "__main__":
    startingBoard = [list("ADEEQS"),
                    list("ELPBTU"),
                    list("DITRUA"),
                    list("EFICRE"),
                    list("CSGEEX"),
                    list("RNULPU"),
                    list("UHKPST"),
                    list("NCNALI")]

    themeWords = ["BURPEE","CRUNCH","DEADLIFT","LUNGE","PLANK","SITUP","SQUAT"]

    spangram = "EXERCISE"

    importantWords = themeWords + [spangram]

    officialSolutions = ["ADEPT","AEDES","AEDILE","ALEE","ALIF","ALIFS","ALIPED","ALIST","ALIT","ALPS","ALTS","ANKH","ANKLE","ANKLUNG","ANKLUNGS","ANKUS","APPEL","APPELS","APPLE","APPS","ARCTIID","AREG","AREIC","ARRIS","ASLEEP","ASPECT","ASPER","ASPERATE","AUCEPS","AUREI","AUREITIES","AUREUS","AURIC","AURIFIED","AURIFIES","AURIS","BEDE","BEDEL","BEEP","BEET","BEETS","BELIE","BELIED","BELIEF","BELIEFS","BELIES","BELT","BEPELT","BETA","BETS","BRIE","BRIER","BRIG","BRIGS","BRIGUE","BRIS","BRISE","BRIT","BRUT","BRUTE","BRUTS","BUAT","BUATS","BURA","BUREAU","BUREAUS","BURIER","BURITI","BURP","BURPED","BURPEE","BURR","BURREL","BURRELS","BUTE","BUTS","CEDE","CEDED","CEDI","CEIL","CEILED","CELS","CEPE","CEPS","CERATE","CERE","CEREUS","CERRIS","CHUG","CHUGS","CHUNK","CHURN","CHURNS","CHUSE","CIEL","CIELS","CIGS","CIRRATE","CITIED","CITIES","CRATE","CRATUR","CREATE","CREE","CREEL","CREELS","CREEP","CREEPS","CREPE","CREPT","CRIER","CRIS","CRISE","CRIT","CRUCK","CRUE","CRUNCH","CRUNKLE","CRURA","CUBE","CUBED","CURAT","CURATE","CURATS","CURB","CURBED","CURE","CURIE","CURN","CURNS","CURPEL","CURR","CURRIE","CURS","CURSE","CURSED","CURSI","CURT","CUTE","CUTS","DALE","DALED","DALI","DALT","DEAD","DEADLIFT","DEAL","DEALT","DEBE","DEBRIS","DEBT","DEBTS","DEBURR","DEBUT","DEBUTS","DEDAL","DEEP","DEEPIE","DEEPIES","DEET","DEETS","DEFI","DEFIED","DEFIER","DEFILADE","DEFILE","DEFILED","DEFIS","DEFT","DEID","DEIF","DEIFIC","DEIFIER","DEIL","DELE","DELED","DELI","DELT","DELTIC","DESI","DESIGN","DIED","DIEL","DIES","DIFS","DIPT","EALE","EATS","EAUS","ECRU","ECURIE","EDIFICE","EDIFIER","EDILE","EDIT","EELS","EGIS","EIDE","EILD","ELECT","ELECTRIFIED","ELECTRIFIES","ELECTRISE","ELECTRISED","ELEGISE","ELEGISED","ELEGIT","ELIDE","ELIDED","ELIDES","ELPEE","EPEE","EPRIS","EPRISE","ERECT","ERECTILE","ERUCT","ETRIER","EUNUCH","EXEAT","EXEATS","EXEC","EXECRATE","EXECUTE","EXERCISE","EXERCISED","EXPECT","EXPEL","EXPELS","FICE","FICTILE","FIELD","FIER","FIERCE","FIERE","FIGS","FILA","FILE","FILED","FISC","GEEP","GEEPS","GEIT","GELEE","GELS","GERE","GIFT","GIRR","GIRT","GIRTS","GLEE","GLEI","GLEIS","GLUE","GLUER","GNUS","GULE","GULP","GULPER","GULPS","GULS","GUNK","GUNS","GUPS","HUCK","HUCKLE","HUER","HUGE","HUGER","HUGS","HULE","HULK","HUNG","HUNGER","HUNK","HUNS","HUPS","ICER","IDEA","IDEAL","IDES","IDLE","IDLED","IGLU","IGLUS","ILEA","ISLE","KALI","KALIS","KLUGE","KNAP","KNAPPER","KNAPPLE","KNAPS","KNUR","KNURS","KUGEL","KUGELS","LADE","LADED","LAKH","LANCH","LANK","LAPPEL","LAPPELS","LAPPER","LAPS","LAST","LEAD","LEEAR","LEEP","LEEPS","LEER","LEET","LEETS","LEGIT","LEGS","LEIR","LEIS","LEPER","LEPID","LEPS","LEPT","LERE","LIED","LIEF","LIEFS","LIES","LIFE","LIFES","LIFT","LIPE","LISLE","LISP","LISPER","LIST","LITS","LITU","LUGE","LUGER","LUGS","LUNG","LUNGE","LUNGEE","LUNGER","LUNGI","LUNGIE","LUNGIS","LUNGS","LUNK","NAPPE","NAPPER","NAPS","NUNS","NURS","NURSE","NURSED","PALS","PAST","PASTIL","PECTISE","PECTISED","PEDAL","PEDALED","PEED","PEEL","PEELED","PEELS","PEER","PEGS","PEISE","PEISED","PELA","PELE","PELITIC","PELT","PERCE","PERE","PEREA","PETAR","PETRIFIED","PETRIFIES","PETS","PIED","PIES","PILA","PILE","PILEA","PILED","PITIER","PLAN","PLANCH","PLANK","PLAST","PLEA","PLEAD","PLEB","PLEBE","PLED","PLEX","PLEXUS","PLIE","PLIED","PLIES","PLUE","PLUG","PLUGS","PLUNGE","PLUNGER","PLUNK","PLUS","PLUSED","PRICE","PRICER","PRIER","PRIG","PRIGS","PRISE","PRISED","PRUTA","PTISAN","PUER","PUGS","PUKA","PULE","PULER","PULK","PULKA","PULKAS","PULP","PULPER","PULPS","PULS","PUNCE","PUNCED","PUNCES","PUNG","PUNGLE","PUNGS","PUNK","PUNKA","PUNKAS","PUNS","PUSLE","PUTS","QUAERE","QUARE","QUAT","QUATE","QUATS","RATE","RATS","RATU","RATUS","RAUCITIES","REATE","RECEPT","RECEPTS","RECIT","RECTI","RECTIFIED","RECTIFIES","RECUR","RECUT","RECUTS","REEL","REELECT","REELS","REEXPEL","REEXPELS","REGS","REIF","REIFIED","REIFIES","REIFS","REIGN","REIGNS","REIS","REPEG","REPEGS","REPEL","REPELS","REPLUNGE","REPP","REPPS","REPS","REUSE","REUSED","RHUS","RICE","RICER","RIEL","RIELS","RIFE","RIFS","RIFT","RIGS","RISE","RUBE","RUBEL","RUBRIC","RUCK","RUCKLE","RUCKUS","RUER","RUNCH","RUNG","RUNGS","RUNKLE","RUNS","RURP","RUTS","SALP","SALT","SANK","SAPPER","SAPPLE","SCRUNCH","SEDILE","SEIDEL","SEIF","SEIL","SEILED","SICE","SIFT","SIGN","SILT","SIRRA","SIRREE","SITUP","SLANK","SLAP","SLAPPER","SLEE","SLEEP","SLEER","SLEPT","SLIT","SLUE","SLUG","SLUGS","SLUNG","SLUNK","SLUSE","SNUCK","SNUG","SPALT","SPAN","SPANK","SPEC","SPECIE","SPECIFIED","SPECIFIES","SPEEL","SPEER","SPEIR","SPEISE","SPELK","SPELUNK","SPEUG","SPEUGS","SPLIT","SPUE","SPUER","SPUG","SPUGS","SPULE","SPUN","SPUNGE","SPUNK","SQUARE","SQUAT","STAR","STARE","STARR","STEED","STEEDED","STEEL","STEELD","STEELED","STEELIE","STEELIES","STEEP","STEEPLE","STEEPLED","STEP","STEPT","STRICT","STRIFE","STRIFES","STRIFT","STRIG","STRIGS","STUB","STUPE","STURE","STURT","SUER","SUKH","SULK","SUNG","SUNK","SUPE","SUPER","SUPERATE","SUPERCITIES","SUPERCUTE","SUPLEX","SUPPER","SUPPLE","SUPPLER","SUPS","SUTURE","TARCEL","TARCELS","TARE","TAUBE","TAURIC","TAUS","TEED","TEEL","TEPID","TICE","TIDE","TIDED","TIDES","TIED","TIER","TIERCE","TIERCEL","TIERCELS","TIES","TIGE","TIGER","TIGS","TILAK","TILDE","TILDES","TILE","TILED","TILS","TIRR","TRICE","TRICEP","TRICEPS","TRIE","TRIER","TRIFID","TRIG","TRIGS","TRISUL","TRISULS","TRITIDE","TRITIDES","TRUCE","TRUE","TRUER","TUBE","TUBED","TUPLE","TUPS","TURTLE","TURTLED","ULEX","ULPAN","UNCE","UNCEDED","UNCES","UNGIRT","UNGLUE","UNHUNG","UNSUPPLE","UNUSED","UPAS","UPLIT","UPPER","UPPERCUT","UPPERCUTS","URATE","UREA","UREIC","URIC","URNS","URPED","USED","UTIS","UTUS"]

    wordTrie = WordTrie()
    with open("english_words.txt", "r") as file:
            for line in file:
                word = line.strip()
                if word:  # Skip empty lines.
                    wordTrie.insert(word)

    for word in officialSolutions:
        wordTrie.insert(word)

    for row in range(len(startingBoard)):
        for col in range(len(startingBoard[0])):
            print(startingBoard[row][col], end=" ")
        print()

    print(validatePuzzle(startingBoard, wordTrie, importantWords))