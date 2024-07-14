import { getCodeChallenge, getCodeVerifier } from "./OAuthHelper";

const redirectUri = 'http://localhost:8888/redirect';
const scope = 'user-read-playback-state user-modify-playback-state';

const authUrl = new URL("https://accounts.spotify.com/authorize")

export async function authorize(clientId: string) {
    let codeVerifier = await getCodeVerifier();
    window.localStorage.setItem("code_verifier", codeVerifier);

    const params =  {
        response_type: 'code',
        client_id: clientId,
        scope,
        code_challenge_method: 'S256',
        code_challenge: await getCodeChallenge(codeVerifier),
        redirect_uri: redirectUri,
    }
    
    authUrl.search = new URLSearchParams(params).toString();
    window.location.href = authUrl.toString();
}