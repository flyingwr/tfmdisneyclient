const is_disney = navigator.userAgent.includes("disneyclient");

const [
	fetch_text,
	key_button,
	key_text,
	key_title,
	auth_container,
	discord_container,
	init_container,
	init_text,
	aside_text,
    main_text,
	result_container,
	result_text,
	hts_btn,
	hts_link] = [
		... ["fetch-text",
			"key-btn",
			"key-text",
			"key-title",
			"auth-container",
			"discord-container",
			"init-container",
			"init-text",
			"aside-text",
            "main-text",
			"fetch-result-container",
			"fetch-result-text",
			"hts-btn",
			"hts-link"
		].map((id) => {
			return document.getElementById(id)
		})
	];

let api_url, auth_url;
let fails = 0;
let fetching = false;

const init_color = "#2e2c29";

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
	fetch_text.textContent = message || translate("connecting");
}

const set_fetch_error_message = function(message) {
	fetch_text.style.color = "red";
	fetch_text.textContent = message || "error";
}

const auth_request = function() {
	if (!fetching) {
		fetching = true;

		set_fetch_message();
		change_elem_display(fetch_text, true);
		change_button_state(key_button);

		const headers = new Headers();
		headers.append("Authorization", `Basic ${window.btoa(key_text.value)}`);

		fetch(auth_url, { headers: headers })
		.then((response) => {
			fetching = false;

			response.json().then((json) => {
				if (response.ok) {
					auth_container.remove();

					let rm_time = 180;

					const sleep = json.sleep;
					if (sleep) rm_time = sleep >= 179 ? 1 : 180 - sleep;

					change_elem_display(result_container, true, "flex");

					result_text.style["user-select"] = "text";
					result_text.textContent = `${translate("token")} ${rm_time} ${translate("minutes")}:\n`;

					const token_url = `${window.location.origin.replace("https", "http")}/transformice?access_token=${json.access_token}`;
					const span = document.createElement("span");
					span.id = "access-token";
					span.textContent = token_url;
					result_text.appendChild(span);

					const img = document.createElement("img");
					img.src = "./images/copy.png";
					img.style.position = "static";
					img.style["max-height"] = "10px";
					img.style["max-width"] = "10px";
					img.style["padding-left"] = "5px";
					img.style.cursor = "pointer";
					img.title = "Copy to clipboard";

					img.onclick = () => {
						window.getSelection().removeAllRanges();

						const range = document.createRange();
						range.setStart(span, 0);
						range.setEnd(span, span.childNodes.length);
						window.getSelection().addRange(range);

						document.execCommand("copy");
					}

					result_text.appendChild(img);

					change_elem_display(hts_btn, true);

					localStorage.setItem("_key", key_text.value);
				} else {
					set_fetch_error_message(json.error);

					fails += 1;
					if (fails >= 8) {
						change_button_state(key_button);
						set_fetch_error_message(translate("temp_block"));

						setTimeout(() => {
							fails = 0;

							change_button_state(key_button, true);
						}, 240000);
					}
				}
			})

			change_button_state(key_button, true);
		}).catch(() => {
			set_fetch_error_message();
		});
	}
}

window.onload = () => {
	key_button.onclick = auth_request;

	const download_btn = document.getElementById("download-btn");
	download_btn.style.display = "none";

    discord_container.innerHTML = translate("buy");
	init_text.textContent = translate("start");
	key_title.textContent = translate("enter_key");
	hts_btn.textContent = translate("hts");
	hts_link.textContent = translate("hts");
    main_text.innerHTML = translate("main");
	aside_text.innerHTML = translate("aside");

	const key = localStorage.getItem("_key");
	if (key) key_text.value = key;

	key_text.addEventListener("keydown", ({key}) => {
		if (key === "Enter") auth_request();
	})

	api_url = new URL("api", window.location.origin);
	auth_url = new URL(`${api_url}/auth`, api_url);
	const discord_url = new URL(`${api_url}/discord`, api_url);
	const update_url = new URL(`${api_url}/update`, api_url)

	fetch(discord_url).then((response) => {
		if (response.ok) {
			change_elem_display(init_container);
			change_elem_display(auth_container, true, "flex");
			change_elem_display(discord_container);

			response.json().then((json) => {
				if (json.names) {
					for (const name of json.names) {
						const img = document.createElement("img");
						img.src = "./images/discord.png";
                        img.style["margin-top"] = "5px";
						discord_container.appendChild(img);

						const small = document.createElement("small");
						small.textContent = name;
                        small.style["margin-top"] = "5px";
                        small.style["padding"] = "0 5px";
						discord_container.appendChild(small);
					}
				}
			});

			if (!is_disney) {
				fetch(update_url).then((response) => {
					if (response.ok) {
						response.json().then((data) => {
							if (data.standalone_url) {
								download_btn.style.display = "flex";
								download_btn.onclick = () => {
									window.open(data.standalone_url, "_blank");
								}
							}
						});
					}
				});
			}
		}
	}).catch(() => {
		set_fetch_error_message();
	});
};