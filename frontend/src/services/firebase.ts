import { initializeApp, getApps, getApp } from 'firebase/app';
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  UserCredential,
  RecaptchaVerifier,
  signInWithPhoneNumber,
  ConfirmationResult
} from 'firebase/auth';
import { authService } from './api';

// Firebase Web Config for TravelPilot
const firebaseConfig = {
  apiKey: "AIzaSyBYM3meS08X13OBTShGm0flNo8uVzWyU1k",
  authDomain: "travel-agent-6d021.firebaseapp.com",
  projectId: "travel-agent-6d021",
  storageBucket: "travel-agent-6d021.firebasestorage.app",
  messagingSenderId: "700890616330",
  appId: "1:700890616330:web:720b496c817c3f7513c5f3"
};

// Initialize Firebase safely
const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();

export const signInWithGoogle = async () => {
  try {
    const result: UserCredential = await signInWithPopup(auth, googleProvider);
    const fbUser = result.user;

    const email = fbUser.email || "traveler@example.com";
    const fullName = fbUser.displayName || email.split("@")[0];

    // Authenticate with TravelPilot backend
    const data = await authService.firebaseLogin(email, fullName);
    return {
      user: data.user,
      token: data.access_token
    };
  } catch (error: any) {
    console.error("Firebase Google Auth error:", error);
    throw error;
  }
};

/**
 * Setup Invisible reCAPTCHA for Firebase Phone SMS OTP
 */
export const setupRecaptcha = (containerId: string = 'recaptcha-container'): RecaptchaVerifier => {
  if (!(window as any).recaptchaVerifier) {
    (window as any).recaptchaVerifier = new RecaptchaVerifier(auth, containerId, {
      size: 'invisible',
      callback: () => {
        // reCAPTCHA solved
      }
    });
  }
  return (window as any).recaptchaVerifier;
};

/**
 * Send real 6-digit SMS OTP via Firebase to any phone number (+91...)
 */
export const sendPhoneOtp = async (phoneNumber: string, containerId: string = 'recaptcha-container'): Promise<ConfirmationResult> => {
  const verifier = setupRecaptcha(containerId);
  return await signInWithPhoneNumber(auth, phoneNumber, verifier);
};

/**
 * Verify SMS OTP and authenticate session
 */
export const verifyPhoneOtp = async (confirmationResult: ConfirmationResult, code: string) => {
  const result = await confirmationResult.confirm(code);
  const fbUser = result.user;
  const phone = fbUser.phoneNumber || "Verified Phone";
  const data = await authService.firebaseLogin(phone, `User ${phone}`);
  return {
    user: data.user,
    token: data.access_token
  };
};
