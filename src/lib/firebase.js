import { initializeApp } from "firebase/app";
import {
    GoogleAuthProvider,
    createUserWithEmailAndPassword,
    getAuth,
    onIdTokenChanged,
    signInWithEmailAndPassword,
    signInWithPopup,
    signOut,
    updateProfile
} from "firebase/auth";

const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({ prompt: "select_account" });

export async function signUpWithFirebase({ name, email, password }) {
    const credential = await createUserWithEmailAndPassword(auth, email, password);
    if (name?.trim()) {
        await updateProfile(credential.user, { displayName: name.trim() });
    }
    const idToken = await credential.user.getIdToken();
    return { user: credential.user, idToken };
}

export async function signInWithFirebase({ email, password }) {
    const credential = await signInWithEmailAndPassword(auth, email, password);
    const idToken = await credential.user.getIdToken();
    return { user: credential.user, idToken };
}

export async function signInWithGoogle() {
    const credential = await signInWithPopup(auth, googleProvider);
    const idToken = await credential.user.getIdToken();
    return { user: credential.user, idToken };
}

export async function signOutFirebase() {
    await signOut(auth);
}

export function subscribeToAuthChanges(callback) {
    return onIdTokenChanged(auth, callback);
}

export { auth };
