const locales = {
	"en": {
		"connecting": "connecting...",
		"enter_key": "Enter your key",
		"minutes": "minutes",
		"open_game": "Open game",
		"send": "Send",
		"soft_input": "Choose XML files to upload",
		"soft_ok": "saved",
		"soft_not_ok": "failed to send",
		"start": "Starting...",
		"token": "Your token has been generated and will be expired in"
	},
	"es": {
		"connecting": "conectando...",
		"enter_key": "Inserta tu llave",
		"minutes": "minutos",
		"open_game": "Abrir juego",
		"send": "Enviar",
		"soft_input": "Seleccione archivos XML para cargar",
		"soft_ok": "guardado",
		"soft_not_ok": "error al enviar",
		"start": "Inicializando...",
		"token": "Tú token ha sido generado y será expirado en"
	},
	"pt": {
		"connecting": "conectando...",
		"enter_key": "Insira sua chave",
		"minutes": "minutos",
		"open_game": "Abrir jogo",
		"send": "Enviar",
		"soft_input": "Selecione arquivos XML para enviar",
		"soft_ok": "salvo",
		"soft_not_ok": "erro ao enviar",
		"start": "Iniciando...",
		"token": "Seu token foi gerado e irá expirar em"
	}
}

const language = navigator.language.split("-")[0];
const translate = function(key) {
	if (language in locales) {
		if (key in locales[language]) {
			return locales[language][key];
		}
	}

	return locales.en[key] || key;
}