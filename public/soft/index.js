window.onload = async () => {
    const files_input = document.getElementById("files-input");
    const select_btn = document.getElementById("select-btn");
    const submit_btn = document.getElementById("submit-btn");

    select_btn.textContent = translate("soft_input");
    submit_btn.textContent = translate("send");
    
    select_btn.onclick = () => {
        files_input.click();
    }

    submit_btn.onclick = async () => {
        if (files_input.files.length) {
            const files = {};

            for (const file of files_input.files) {
                const name = file.name.replace(".txt", "");

                const text = await file.text();
                if (text)
                {
                    const xml = text.trim();
                    if (xml.startsWith("<C><P") && xml.endsWith("</Z></C>")) {
                        files[name[0] === "@" ? name : `@${name}`] = xml;
                    }
                }
            }

            if (Object.keys(files).length) { 
                const form_data = new FormData();
                form_data.append("soft", JSON.stringify(files));
        
                const match = window.location.href.match(/access_token=(.*)/);
                const token_query = match ? `?access_token=${match[1]}` : "";

                fetch(`${window.origin}/data${token_query}`, {
                    method: "POST",
                    body: form_data
                }).then((response) => {
                    const result_el = document.getElementById("result");
                    result_el.textContent = response.ok ? translate("soft_ok") : translate("soft_not_ok");
                    result_el.style.color = response.ok ? "lime": "red";
                })
            }
        }
    }
}