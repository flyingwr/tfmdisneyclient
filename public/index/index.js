const [
	fetch_text,
	key_button,
	key_text,
	auth_container,
	discord_container,
	init_container,
	init_text,
	small_text,
	uuid_text,
	version_text,
	result_container,
	result_text,
	open_game_btn] = [
		... ["fetch-text",
			"key-btn",
			"key-text",
			"auth-container",
			"discord-container",
			"init-container",
			"init-text",
			"small-text",
			"uuid-text",
			"version-text",
			"fetch-result-container",
			"fetch-result-text",
			"open-btn"
		].map((id) => {
			return document.getElementById(id)
		})
	];

let api_url, auth_url, discord_url;
let fetching = false;
let init_color = "#2e2c29";

const change_button_state = function(elem, enabled) {
	elem.style["pointer-events"] = enabled ? "auto" : "none";
	elem.style.cursor = enabled ? "pointer" : "default";
	elem.style.color = enabled ? init_color : "gray";
}

const change_elem_display = function(elem, visible, type) {
	const style = window.getComputedStyle(elem, null);
	if (style !== null) {
		if (style.visibility === "hidden") {
			return elem.style.visibility = "visible";
		}
	}
	if (visible) {
		type = type || "initial";
	} else {
		type = type || "none";
	}
	elem.style.display = type;
};

const set_fetch_message = function(message) {
	fetch_text.style.color = "inherit";
	fetch_text.textContent = message || "connecting...";
}

const set_fetch_error_message = function(message) {
	fetch_text.style.color = "red";
	fetch_text.textContent = message || "Error: server unavailable";
}

const auth_request = function() {
	if (!fetching) {
		fetching = true;

		set_fetch_message();
		change_elem_display(fetch_text, true);
		change_button_state(key_button);

		const params = {key: key_text.value};		
		if (uuid_text.value) params.uuid = uuid_text.value;
		if (version_text.value) params.version = version_text.value;

		fetch(`${auth_url}?${new URLSearchParams(params)}`, {
			"User-Agent": `DisneyClient${version_text ? "/" + version_text : ""}`
		}).then((response) => {
			fetching = false;

			response.json().then((json) => {
				if (response.ok) {
					auth_container.remove();

					const sleep = json.sleep;

					let rm_time = 60
					if (sleep) rm_time = sleep >= 59 ? 1 : 60 - sleep;

					change_elem_display(result_container, true, "flex");
					result_text.style["user-select"] = "text";
					result_text.textContent = `Your token has been generated and will be expired in ${rm_time} minutes:\n${window.location.origin}/transformice?access_token=${json.access_token}`;

					if (navigator.userAgent.includes("Electron")) {
						open_game_btn.style.padding = "5px 5px";
						change_elem_display(open_game_btn, true);
					}
				} else if (response.status === 401) {
					set_fetch_error_message(json.error);
				} else if (response.status === 406) {
					set_fetch_error_message(json.error);
				}
			})

			change_button_state(key_button, true);
		}).catch((error) => {
			set_fetch_error_message();
		});
	}
}

key_button.onclick = () => {
	auth_request();
};

window.onload = () => {
	key_text.addEventListener("keydown", ({key}) => {
		if (key === "Enter") auth_request();
	})

	api_url = new URL("api", window.location.origin);
	auth_url = new URL(`${api_url}/auth`, api_url);
	discord_url = new URL(`${api_url}/discord`, api_url);

	fetch(discord_url).then((response) => {
		if (response.ok) {
			change_elem_display(init_container);
			change_elem_display(auth_container, true, "flex");
			change_elem_display(discord_container);

			response.text().then((text) => {
				small_text.textContent = text;
			});
		}
	}).catch((error) => {
		set_fetch_error_message();
	});
};