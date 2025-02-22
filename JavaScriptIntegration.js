const ROWS = 8
const COLS = 6

YELLOW = 'rgb(255, 234, 0)'
BLUE = 'rgb(173, 216, 230)'
MANUAL_DICT = {}

const generate_empty_table = () => {
    const table = document.getElementById("table")
    for (let i = 0; i < ROWS; i++) {
        const new_element = document.createElement('tr')
        for (let j = 0; j < COLS; j++) {
            const entry = document.createElement('td')
            entry.textContent = "."
            entry.id = `p${i*6+j}`

            new_element.appendChild(entry)
        }
        table.appendChild(new_element)
    }

}

const fill_hidden_fields = (spangram, spangramloc, words, loc) => {
    document.getElementById('h_spangram').value = spangram
    document.getElementById('spangramloc').value = spangramloc
    document.getElementById('words').value = words
    document.getElementById('loc').value = loc
}

const draw_word = (locs, color) => {
    for (let i = 0; i < locs.length; i++) {
        const loc = locs[i];
        drawTransparentCircleAboveEntry(`p${loc}`, "permanentCanvas", color,  1)
    }
    for (let i = 0; i < locs.length - 1; i++) {
        const loc = locs[i];
        const loc1 = locs[i+1];
        drawLineBetweenEntries(`p${loc}`, `p${loc1}`, "permanentCanvas", color, 1)
    }
}

const fill_table = (spangram, spangramloc, words, loc) => {
    const arr_sloc = spangramloc.split("|")
    const arr_loc = loc.split("|")
    const arr_words = words.split("|")
    const raw_words = words.replaceAll("|","")
    

    arr_sloc.forEach((loc, i) => {
        const entry = document.getElementById(`p${loc}`)
        entry.textContent = spangram[i].toUpperCase()
    });
    arr_loc.forEach((loc, i) => {
        const entry = document.getElementById(`p${loc}`)
        entry.textContent = raw_words[i].toUpperCase()
    });
    set_temp()
    set_canvas()

    draw_word(arr_sloc, YELLOW)

    for (let i = 0; i < arr_loc.length; i++) {
        const loc = arr_loc[i];
        drawTransparentCircleAboveEntry(`p${loc}`, "permanentCanvas", BLUE,  1)
    }

    let at = 0
    for (let i = 0; i < arr_words.length; i++) {
        const word = arr_words[i]
        for (let j = 0; j < word.length-1; j++) {
            const loc = arr_loc[at]
            const loc1 = arr_loc[at+1]
            drawLineBetweenEntries(`p${loc}`, `p${loc1}`, "permanentCanvas", BLUE, 1)
            at = at + 1
        }
        at = at + 1
    }

    document.getElementById("url").dispatchEvent(new Event('input'))
    document.getElementById("generate-submit").innerText = "Regenerate"
    document.getElementById("manual").innerText = "Edit Manually"
}

const get_letter_count = () => {
    const spangram = document.getElementById("spangram")
    const container = document.getElementById("text-container")
    const words = container.querySelectorAll("input")

    let count = spangram.value?.length ?? 0
    words.forEach(word => {
        count += word.value?.length ?? 0
        if (word.value){
            word.value = word.value.toLowerCase()
        }
    });

    return count
}

const update_char_string = () => {
    const char_element = document.getElementById("char_str")
    const count = get_letter_count()
    const spangram_count = document.getElementById("spangram").value.length
    let string = `You have ${count} letters. `
    if (count < ROWS * COLS){
        string += `You need ${ROWS * COLS - count} more. `
    }
    if (count > ROWS * COLS){
        string += `You need ${count - ROWS * COLS} less. `
    }
    if (spangram_count < 6){
        string += `<br>Spangram needs ${6 - spangram_count} more letters. `
    }
    
    char_element.innerHTML = string

    if (count !== 48 || spangram_count < 6){
        char_element.style.color = 'red'
    }
    else{
        char_element.style.color = 'green'
    }

    BLOCK = update_warnings()
    
    if (count === 48 && !BLOCK){
        document.getElementById("generate-submit").disabled = false
        document.getElementById("manual").disabled = false
    }
    else{
        document.getElementById("generate-submit").disabled = true
        document.getElementById("manual").disabled = true
    }

    const all_words = get_all_words()
    MANUAL_DICT = {}
    all_words.forEach((word) => {
        MANUAL_DICT[word] = []
    })

    
    reset_table()
    set_url_dirty()
}

const update_warnings = () => {
    // Repeat words
    REPEAT = false
    // Word too short
    SHORT = false
    // Word contains something other than letters
    NON_LETTER = false
    // Did not change theme
    THEME = document.getElementById("user-theme").innerHTML === "Enter Theme"
    // Did not change title
    TITLE = document.getElementById("user-title").innerHTML === "Enter Title"

    // Contains Empty Word
    EMPTY = has_empty_word()

    // Should Block generation
    BLOCK = false
    const all_words = get_all_words()
    const word_set = new Set();
    for(const word of all_words){
        if (word_set.has(word)) {
            REPEAT = true
        }
        word_set.add(word);
        if (word.length < 3){
            SHORT = true
        }
        if (/[^a-zA-Z]/.test(word)){
            NON_LETTER = true
        }
    }
    const error_element = document.getElementById("errors_words")
    const warning_element = document.getElementById("warnings_words")
    
    let errors = ""
    let warnings = ""

    if (REPEAT) {
        errors += "ERROR: Can not have repeated words.<br>"
        BLOCK = true
    }
    if (EMPTY) {
        errors += "ERROR: Can not have empty words.<br>"
        BLOCK = true
    }
    if (SHORT) {
        warnings += "WARNING: Words should be longer than 3 characters.<br>"
    }
    if (NON_LETTER) {
        warnings += "WARNING: Best for words not to have non-letters (especially spaces).<br>"
    }
    if (THEME) {
        warnings += "WARNING: Consider modifying the theme.<br>"
    }
    if (TITLE) {
        warnings += "WARNING: Consider modifying the title.<br>"
    }

    error_element.innerHTML = errors
    warning_element.innerHTML = warnings

    return BLOCK
}

const append_new_input_element = () => {
    const parent = document.getElementById("text-container")
    const span = document.getElementById("spangram")
    span.addEventListener('input', update_char_string)
    const children_containers = Array.from(parent.childNodes).filter(child => child.nodeType === Node.ELEMENT_NODE && child.tagName === "DIV");
    children_containers.forEach(child_container => {
        const input = child_container.querySelector('input')
        input.addEventListener('input', update_char_string)
        const delete_button = child_container.querySelector('button')
        delete_button.addEventListener('click', delete_current_input)
    });

    update_char_string()
}

const url_lookup = () => {
    const form = document.getElementById("save")
    const url = document.getElementById("url")
    url.value = url.value.replace(/\s/g, '')
    const url_val = url.value
    const disp = document.getElementById("url-valid")
    const submit = document.getElementById("save-submit")
    if (!url_val){
        disp.innerHTML = "Url must not be blank"
        disp.style.color = 'red'
        submit.hidden = true
        return 
    }
    fetch("url_check", {
        method: "POST",
        body: JSON.stringify({
            'val': url_val
        }),
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value,
        }
    })
    .then(response => response.json())
    .then(data => {
        const exists = data['exists']
        const disp = document.getElementById("url-valid")
        if (exists){
            disp.innerHTML = "Url Already Exists, Try Again"
            submit.hidden = true
            disp.style.color = 'red'
        }
        else {
            disp.innerHTML = "Good!"
            disp.style.color = 'green'
            if (is_dict_full()){ //TODO
                submit.hidden = false
            }
        }
    })
    .catch(e => {
        console.error("Error with URL:", e)
    })
}

const set_url_dirty = () => {
    const disp = document.getElementById("url-valid")
    const submit = document.getElementById("save-submit")
    disp.innerHTML = ""
    document.getElementById("check-url").hidden = false
    submit.hidden = true

    update_table_full()
}

const set_default_url = () => {
    const output = document.getElementById("url")
    const title = document.getElementById("title")
    const theme = document.getElementById("theme")

    output.value = title.value.replace(/[^a-zA-Z]/g, "") + "-" + theme.value.replace(/[^a-zA-Z]/g, "")
}

const check_url_event = () => {
    document.getElementById("check-url").hidden = true
    url_lookup()
}

const get_element_id_number_from_event = (e) => {
    return Number(e.srcElement.id.slice(1))
}

const delete_current_input = (e) => {
    const element_id = get_element_id_number_from_event(e)
    if (document.getElementById("numw").value == 1){
        return
    }
    const container = document.getElementById("text-container")
    const inputs = container.querySelectorAll("input")
    const words = Array.from(inputs).map(input => input.value);

    container.removeChild(container.lastChild)
    document.getElementById("numw").value = Number(document.getElementById("numw").value) - 1

    for (let i = 0; i < words.length-2-element_id+1; i++) {
        const element = document.getElementById(`w${i+element_id}`)
        element.value = words[i+element_id+1]
    }
    update_char_string()
    set_url_dirty()    
}

const create_a_row = (row_num, value="") => {
    const container = document.getElementById("text-container")
    const new_div = document.createElement("div")
    new_div.className = "text-input"
    const new_input = document.createElement("input")
    new_input.type = "text"
    new_input.name = `w${row_num}`
    new_input.id = `w${row_num}`
    new_input.className = "form-control"
    new_input.value = value
    const new_button = document.createElement("button")
    new_button.type = "button"
    new_button.className = "delete-button"
    new_button.id = `d${row_num}`
    new_button.innerText = "X"

    new_div.appendChild(new_input)
    new_div.appendChild(new_button)
    container.appendChild(new_div)
    append_new_input_element()

}

const serial_to_dict = (spangram, spangramloc, words, loc) => {
    MANUAL_DICT = {}
    MANUAL_DICT[spangram.toUpperCase()] = spangramloc.split("|").map(Number)

    let at = 0
    const word_arr = words.split("|")
    const loc_arr = loc.split("|")
    for (let i = 0; i < word_arr.length; i++) {
        const word = word_arr[i];
        MANUAL_DICT[word.toUpperCase()] = []
        for (let c = 0; c < word.length; c++) {
            MANUAL_DICT[word.toUpperCase()].push(Number(loc_arr[at]))
            at += 1
        }
    }
    console.log(MANUAL_DICT)
}

const call_generate = (e) => {
    e.preventDefault(); // Prevent the default form submission
    form = document.getElementById("generate")
    const formData = new FormData(form);
    set_url_dirty()

    document.getElementById("generate-submit").disabled = true
    document.getElementById("manual").disabled = true
    document.getElementById("loading").hidden = false
    fetch("generate", {
        method: "POST",
        body: new URLSearchParams(formData),
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value,
        }
    })
    .then(response => response.json()) // Convert the response to JSON
    .then(data => {
        fill_hidden_fields(data['spangram'], data['spangramloc'], data['words'], data['loc'])
        fill_table(data['spangram'], data['spangramloc'], data['words'], data['loc'])
        serial_to_dict(data['spangram'], data['spangramloc'], data['words'], data['loc'])
        set_url_dirty()
        document.getElementById("generate-submit").disabled = false
        document.getElementById("manual").disabled = false
        document.getElementById("loading").hidden = true
    })
    .catch(error => {
        console.error("Error:", error);
        document.getElementById("generate-submit").disabled = false
        document.getElementById("manual").disabled = false
        document.getElementById("loading").hidden = true
    });
}

const add_a_word = () => {
    const num_words = document.getElementById("numw")
    num_words.value = Number(num_words.value) + 1
    const val = Number(num_words.value)
    create_a_row(val-1)
    set_url_dirty()
}

const clear_all_words = () => {
    const container = document.getElementById("text-container")
    while (container.firstChild){
        container.removeChild(container.firstChild)
    }
    const num_words = document.getElementById("numw")
    num_words.value = 1

    create_a_row(0)
}

const get_all_words = () => {
    const container = document.getElementById("text-container")
    const words = container.querySelectorAll("input")
    const spangram = document.getElementById("spangram")

    const word_array = []
    if (spangram.value) {
        word_array.push(spangram.value.toUpperCase())
    }
    words.forEach(word => {
        if (word.value){
            word_array.push(word.value.toUpperCase())
        }
    });
    return word_array
}

const has_empty_word = () => {
    const container = document.getElementById("text-container")
    const words = container.querySelectorAll("input")
    for(word of words){
        if (!word.value){
            return true
        }
    }
    return false
}

const find_word_coordinates = (board, word) => {
    const rows = board.length;
    const cols = board[0].length;
    const word_len = word.length;

    const dfs = (x, y, at, path) => {
        if (at === word_len) {
            return path;
        }
        if (!(0 <= x && x < rows && 0 <= y && y < cols)) {
            return null;
        }
        if (board[x][y] !== word[at]) {
            return null;
        }
        if (path.some(([px, py]) => px === x && py === y)) {
            return null;
        }

        path.push([x, y]);

        const directions = [
            [-1, -1], [-1, 0], [-1, 1],
            [0, -1],         [0, 1],
            [1, -1], [1, 0], [1, 1]
        ];

        for (const [dx, dy] of directions) {
            const result = dfs(x + dx, y + dy, at + 1, path);
            if (result) {
                return result;
            }
        }

        path.pop();
        return null;
    }

    for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols; j++) {
            if (board[i][j] === word[0]) {
                const path = dfs(i, j, 0, []);
                if (path) {
                    return path;
                }
            }
        }
    }

    return null;
}

const coord_to_pos = (i, j) => {
    return i * 6 + j
}

const pos_in_manual_dict = (pos) => {
    for (const key of Object.keys(MANUAL_DICT)) {
        if (MANUAL_DICT[key].includes(pos)) {
            return true;
        }
    }
    return false;
}

const get_unplaced_words = () => {
    const words = []

    Object.keys(MANUAL_DICT).forEach(key => {
        if (MANUAL_DICT[key].length === 0){
            words.push(key)
        }
    })

    return words
}

const render_manual_dict = () => {
    set_temp()
    set_canvas()
    const spangram = document.getElementById("spangram").value
    Object.keys(MANUAL_DICT).forEach(key => {
        const locs = MANUAL_DICT[key]
        const color = key.toUpperCase() === spangram.toUpperCase() ? YELLOW : BLUE
        if (locs.length !== 0) {
            draw_word(locs, color)
        }
    })
    
}

const get_word_at_pos = (pos) => {
    for (const key of Object.keys(MANUAL_DICT)) {
        if (MANUAL_DICT[key].includes(pos)) {
            return key;
        }
    }
    throw Error("Event Listeners Not Removed or Manual Dict not updated")
}

const delete_word_at_pos = (e) => {
    const clicked_pos = get_element_id_number_from_event(e)
    const word = get_word_at_pos(clicked_pos)
    const positions = MANUAL_DICT[word]
    positions.forEach(pos => {
        const element = document.getElementById(`p${pos}`)
        element.innerHTML = "."
        element.removeEventListener("click", delete_word_at_pos)
        element.setAttribute("contenteditable", "true")
    })
    MANUAL_DICT[word] = []
    render_manual_dict()
    set_url_dirty()
}

const is_dict_full = () => {
    if (Object.keys(MANUAL_DICT).length === 0){
        return false
    }
    if (get_letter_count() != 48){
        return false
    }
    for (const key of Object.keys(MANUAL_DICT)) {
        if (MANUAL_DICT[key].length === 0) {
            return false;
        }
    }
    return true;
}

const place_a_letter = (e) => {
    const cell = e.target
    const data = e.data
    if (e.data === null) {
        return
    }
    cell.innerText = data.toUpperCase()
    
    const rows = 8
    const cols = 6
    const array = new Array(rows)
    for(let i = 0; i < rows; i++){
        array[i] = new Array(cols)
        for(let j = 0; j < cols; j++){
            const pos = coord_to_pos(i, j)
            const value = document.getElementById(`p${pos}`).innerHTML
            if (pos_in_manual_dict(pos) || value === "."){
                array[i][j] = "|"
            }
            else{
                array[i][j] = value
            }
        }
    }

    const unplaced_words = get_unplaced_words()
    for (let i = 0; i < unplaced_words.length; i++) {
        const word = unplaced_words[i];
        const coords = find_word_coordinates(array, word)
        if (coords === null) {
            continue
        }
        coords.forEach(c => {
            const pos = coord_to_pos(c[0], c[1])
            MANUAL_DICT[word].push(pos)
            const element = document.getElementById(`p${pos}`)
            element.setAttribute('contenteditable', 'false')
            element.addEventListener('click', delete_word_at_pos)
        })
        break
    }

    render_manual_dict()

    set_url_dirty()

}

const smart_move = (e) => {
    console.log(e)
    let pos = get_element_id_number_from_event(e)
    switch(e.key) {
        case 'Enter':
            pos += 6
            e.preventDefault()
            break;
        case 'ArrowUp':
            pos -= 6
            e.preventDefault()
            break;
        case 'ArrowDown':
            pos += 6
            e.preventDefault()
            break;
        case 'ArrowLeft':
            pos -= 1
            e.preventDefault()
            break;
        case 'ArrowRight':
            pos += 1
            e.preventDefault()
            break;
        case 'Backspace':
            e.srcElement.innerHTML = "."
    }
    if (0 <= pos && pos <= 47){
        document.getElementById(`p${pos}`).focus()
    }

    set_url_dirty()
}

const update_table_full = () => {
    const e = document.getElementById("full-indicator")
    if (is_dict_full()){
        e.innerHTML = "Table Full!"
        e.style.color = 'green'
    }
    else {
        e.innerHTML = "Table Not Full!"
        e.style.color = 'red'
    }
}

const init_manual_mode = () => {

    const table_elements = document.querySelectorAll("td")

    table_elements.forEach((element) => {
        element.setAttribute('contenteditable', 'true')
        element.addEventListener("input", place_a_letter)
        element.addEventListener("keydown", smart_move)
        element.addEventListener("paste", (e) => {
            e.preventDefault()
        })
    })

    for (let i = 0; i < 48; i++) {
        const element = document.getElementById(`p${i}`)
        if (pos_in_manual_dict(i)){
            element.setAttribute('contenteditable', 'false')
            element.addEventListener('click', delete_word_at_pos)
        }      
    }

    enter_manual_mode_buttons()
    set_url_dirty()

    resize()
}

const dict_to_hidden = () => {
    const spangram = document.getElementById("spangram").value.toUpperCase()
    const spangramloc = MANUAL_DICT[spangram].join("|")
    const words_arr = []
    const loc_arr = []
    Object.keys(MANUAL_DICT).forEach(key => {
        if (key !== spangram){
            words_arr.push(key)
            MANUAL_DICT[key].forEach(pos => {
                loc_arr.push(pos)
            })
        }
    })
    const words = words_arr.join("|")
    const loc = loc_arr.join("|")
    return [spangram, spangramloc, words, loc]
}

const enter_manual_mode_buttons = () => {
    document.getElementById("manual").disabled = true
    document.getElementById("manual-button-group").hidden = false
    document.getElementById("manual-info").hidden = false
    document.getElementById("generate-submit").disabled = true
    document.getElementById("add").disabled = true
    document.getElementById("clear").disabled = true
    document.getElementById("check-url").disabled = true

    const container = document.getElementById("text-container")
    const words = container.querySelectorAll("input")
    const spangram = document.getElementById("spangram")

    words.forEach(word => {
        word.disabled = true
    })
    spangram.disabled = true

    const delete_buttons = document.querySelectorAll(".delete-button")

    delete_buttons.forEach(button => {
        button.disabled = true
    })

}

const reset_table = () => {
    const table = document.getElementById("table")
    table.innerHTML = ''
    generate_empty_table()
    set_temp()
    set_canvas()
}

const exit_manual_mode_buttons = () => {

    document.getElementById("manual").disabled = false
    document.getElementById("manual-button-group").hidden = true
    document.getElementById("manual-info").hidden = true
    document.getElementById("generate-submit").disabled = false
    document.getElementById("add").disabled = false
    document.getElementById("clear").disabled = false
    document.getElementById("check-url").disabled = false

    const container = document.getElementById("text-container")
    const words = container.querySelectorAll("input")
    const spangram = document.getElementById("spangram")

    words.forEach(word => {
        word.disabled = false
    })
    spangram.disabled = false

    const delete_buttons = document.querySelectorAll(".delete-button")

    delete_buttons.forEach(button => {
        button.disabled = false
    })

    const table_elements = document.querySelectorAll("td")

    table_elements.forEach((element) => {
        element.setAttribute('contenteditable', 'false')
        element.removeEventListener("input", place_a_letter)
        element.removeEventListener("keydown", smart_move)
        element.removeEventListener("paste", (e) => {
            e.preventDefault()
        })
        element.removeEventListener("click", delete_word_at_pos)
    })
    resize()
}

const save_changes = () => {
    const [spangram, spangramloc, words, loc] = dict_to_hidden()
    fill_hidden_fields(spangram, spangramloc, words, loc)

    exit_manual_mode_buttons()
}

const clear_board = () => {
    Object.keys(MANUAL_DICT).forEach(key => {
        MANUAL_DICT[key] = []
    })
    render_manual_dict()
    reset_table()
    exit_manual_mode_buttons()
    init_manual_mode()
    set_url_dirty()
}

document.addEventListener("DOMContentLoaded", function() {
    append_new_input_element()
    generate_empty_table()
    document.getElementById("numw").value = "1"

    document.getElementById("generate").addEventListener("submit", call_generate);

    document.getElementById("add").addEventListener("click", add_a_word)

    document.getElementById("clear").addEventListener("click", clear_all_words)

    document.getElementById("url").addEventListener("input", set_url_dirty)

    document.getElementById("manual").addEventListener("click", init_manual_mode)

    document.getElementById("save_manual").addEventListener("click", save_changes)
    document.getElementById("clear_board").addEventListener("click", clear_board)
    document.getElementById("user-title").addEventListener("input", () => {
        document.getElementById("title").value = document.getElementById("user-title").textContent
        update_warnings()
        set_default_url()
        set_url_dirty()
        
    })

    document.getElementById("user-theme").addEventListener("input", () => {
        document.getElementById("theme").value = document.getElementById("user-theme").textContent
        update_warnings()
        set_default_url()
        set_url_dirty()
    })

    document.getElementById("user-title").dispatchEvent(new Event('input'))
    document.getElementById("user-theme").dispatchEvent(new Event('input'))

    document.getElementById("check-url").addEventListener("click", check_url_event)

    window.addEventListener('resize', resize)
    window.addEventListener('scroll', resize)

    var navbar = document.getElementById('navbarNav');

    if ($.fn.collapse) {
        $(navbar).on('shown.bs.collapse', resize);

        $(navbar).on('hidden.bs.collapse', resize);
    } else {
        console.error('Bootstrap collapse plugin not loaded');
    }

    reset_table() // Weird bug if not here
})

