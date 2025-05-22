import { getAuth } from "firebase/auth";

const auth = getAuth();
const user = auth.currentUser;                     // Current signed‑in user
const idToken = await user.getIdToken(/* forceRefresh */ true);
console.log(idToken);
