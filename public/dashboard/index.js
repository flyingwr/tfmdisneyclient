const api_url = new URL("api", window.location.origin);
const fetch_url = new URL(`${api_url}/fetch`, api_url);
const maps_url = new URL("mapstorage", window.location.origin);
const data_url = new URL("data", window.location.origin);

const menu = document.getElementById("menu");
for (const elem of menu.getElementsByTagName("a")) {
    elem.onclick = () => {
        for (const link of menu.getElementsByTagName("a")) {
            document.getElementById(link.href.match(/#(.*)/)[1]).classList.remove("active");
            link.classList.remove("active");
        }
        document.getElementById(elem.href.match(/#(.*)/)[1]).classList.add("active");
        elem.classList.add("active");
    }
}

const [ config_elem, maps_elem, soft_elem ] = [
    ... ["config", "maps", "soft"]
].map(id => {
    return document.getElementById(id)
});

fetch(fetch_url).then(async (response) => {
    if (response.ok) {
        response.json().then(async (json) => {
            const elem = document.getElementById("user");

            const user = json.user;
            if (user) {
                elem.innerHTML = `
                    <p>Key: ${user.key}</p>
                    <p>Premium level: ${user.premium_level}</p>
                `;
                if (user.access_token) elem.innerHTML += `<p>Token URL: ${user.access_token}</p>`;
                elem.innerHTML += `<p>Permission to modify autoplay maps: ${user.maps_allowed}</p>`;

                download_config(user.access_token);
                download_maps(user.access_token);
                download_soft(user.access_token);
            }
        });
    }
});

const download_config = async (access_token) => {
    config_elem.innerHTML = "<p>Downloading</p>";

    fetch(`${data_url}?${new URLSearchParams({access_token: access_token, config: 0})}`).then(async (response) => {
        const reader = response.body.getReader();
        const total = +response.headers.get("Content-Length");
        let loaded = 0;

        let [ decoder, text ] = [new TextDecoder("utf-8"), ""];
    
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
    
            text += decoder.decode(value)

            loaded += value.byteLength;
            config_elem.innerHTML = `<p>Downloading... (${Math.round(loaded / total * 100)}%)</p>`;
        }

        return JSON.parse(text);
    }).then(json => {
        config_elem.innerHTML = "<p>Any changes made here won't affect the game until it's restarted.</p>";

        for (const key in json) {
            const object = json[key];

            let value = typeof(object) == "number" ? object : object.value;
            if (object.state !== null && object.state !== undefined || value) {
                let html = "<fieldset class='shortcut'>";
                html += `<legend>${translate(key)}${object.shortcut ? ` [${object.shortcut}]` : ""}</legend>`;
                if (value) {
                    html += `
                        <label for="${key}">Value:</label>
                        <input type="text" id="${key}" value=${value} maxlength="9" size="1">
                    `;
                }

                if (object.hasOwnProperty("state")) {
                    html += `
                        <input type="checkbox" id="${key}-chkbox" ${object.state ? "checked" : ""}>
                        <label for="${key}-chkbox">Enable</label>
                    `;
                }

                config_elem.innerHTML += `${html}</fieldset><br>`;
            }
            
            console.log(key, object);
        }
    });
}

const download_maps = async (access_token) => {
    maps_elem.innerHTML = "<p>Downloading</p>";

    fetch(`${maps_url}?${new URLSearchParams({access_token: access_token})}`).then(async (response) => {
        const reader = response.body.getReader();
        const total = +response.headers.get("Content-Length");
        let loaded = 0;
    
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
    
            loaded += value.byteLength;
            maps_elem.innerHTML = `<p>Downloading... (${Math.round(loaded / total * 100)}%)</p>`;
        }
    });
}

const download_soft = async (access_token) => {
    soft_elem.innerHTML = "<p>Downloading</p>";

    fetch(`${data_url}?${new URLSearchParams({access_token: access_token, soft: 0})}`).then(async (response) => {
        const reader = response.body.getReader();
        const total = +response.headers.get("Content-Length");
        let loaded = 0;
    
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
    
            loaded += value.byteLength;
            soft_elem.innerHTML = `<p>Downloading... (${Math.round(loaded / total * 100)}%)</p>`;
        }
    });
}