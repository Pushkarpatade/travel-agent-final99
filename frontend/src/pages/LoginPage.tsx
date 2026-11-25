import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Phone, ArrowRight, Loader2, Compass, ShieldCheck, KeyRound, Sparkles, CheckCircle2, Smartphone } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { Navbar } from '../components/Navbar';
import { sendPhoneOtp, verifyPhoneOtp } from '../services/firebase';

export const LoginPage: React.FC = () => {
  const [authMode, setAuthMode] = useState<'email' | 'phone'>('email');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [otp, setOtp] = useState('');
  const [demoOtp, setDemoOtp] = useState('');
  const [confirmationResult, setConfirmationResult] = useState<any>(null);
  const [isOtpStep, setIsOtpStep] = useState(false);
  const [error, setError] = useState('');
  const [isSendingOtp, setIsSendingOtp] = useState(false);

  const { sendOtp, verifyOtp, googleSignIn, isLoading } = useAuth();
  const navigate = useNavigate();

  // Step 1: Initiate login with Email 2-Step OTP Verification
  const handleInitiateEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSendingOtp(true);

    try {
      const res = await sendOtp(email);
      setDemoOtp(res.demo_otp || '999999');
      setIsOtpStep(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send verification code.');
    } finally {
      setIsSendingOtp(false);
    }
  };

  // Step 1b: Initiate login with Real Firebase SMS OTP
  const handleInitiatePhoneLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSendingOtp(true);

    const formattedPhone = phoneNumber.startsWith('+') ? phoneNumber.trim() : `+91${phoneNumber.trim()}`;

    try {
      const confirmation = await sendPhoneOtp(formattedPhone, 'recaptcha-container');
      setConfirmationResult(confirmation);
      setIsOtpStep(true);
    } catch (err: any) {
      console.error('Firebase SMS error:', err);
      setError(err.message || 'Failed to send SMS OTP. Please check phone number with country code (+91...).');
    } finally {
      setIsSendingOtp(false);
    }
  };

  // Step 2: Verify OTP and finalize login
  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      if (authMode === 'phone' && confirmationResult) {
        // Verify real SMS OTP via Firebase
        const result = await verifyPhoneOtp(confirmationResult, otp);
        localStorage.setItem('tp_auth_token', result.token);
        localStorage.setItem('tp_user', JSON.stringify(result.user));
        window.location.href = '/dashboard';
      } else {
        // Verify Email OTP
        await verifyOtp(email, otp, undefined, password);
        navigate('/dashboard');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Invalid or expired OTP code.');
    }
  };

  // 1-Click Firebase / Google Auto-Authentication with Real Google Popup
  const handleFirebaseLogin = async () => {
    setError('');
    try {
      await googleSignIn();
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Google sign-in error:', err);
      setError(err.message || 'Firebase Google Sign-In failed or popup was closed.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      <Navbar />

      {/* Invisible reCAPTCHA container for Firebase Phone SMS */}
      <div id="recaptcha-container"></div>

      <div className="flex-1 flex items-center justify-center p-4 py-8 sm:py-12">
        <div className="w-full max-w-md p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-xl transition-all">
          {/* Header */}
          <div className="text-center mb-6">
            <div className="w-12 h-12 rounded-2xl bg-cyan-100 border border-cyan-200 flex items-center justify-center text-cyan-700 mx-auto mb-3 shadow-xs">
              <Compass className="w-6 h-6" />
            </div>
            <h2 className="text-2xl font-black text-slate-900 tracking-tight">
              {isOtpStep ? '2-Step Verification' : 'Welcome Back'}
            </h2>
            <p className="text-xs sm:text-sm font-medium text-slate-500 mt-1">
              {isOtpStep
                ? `Enter the 6-digit code sent to ${authMode === 'phone' ? phoneNumber : email}`
                : 'Sign in to access your autonomous AI travel itineraries'}
            </p>
          </div>

          {/* Security Badge */}
          <div className="mb-4 flex items-center justify-center gap-2 py-1.5 px-3 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-bold">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Resend Email OTP & Firebase SMS Active</span>
          </div>

          {/* Mode Switcher Tabs (Email OTP vs Mobile SMS OTP) */}
          {!isOtpStep && (
            <div className="grid grid-cols-2 p-1 mb-5 bg-slate-100 rounded-xl border border-slate-200">
              <button
                type="button"
                onClick={() => setAuthMode('email')}
                className={`flex items-center justify-center gap-2 py-2 text-xs font-bold rounded-lg transition-all ${
                  authMode === 'email'
                    ? 'bg-white text-cyan-800 shadow-xs'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                <Mail className="w-3.5 h-3.5" />
                <span>Email + OTP</span>
              </button>
              <button
                type="button"
                onClick={() => setAuthMode('phone')}
                className={`flex items-center justify-center gap-2 py-2 text-xs font-bold rounded-lg transition-all ${
                  authMode === 'phone'
                    ? 'bg-white text-cyan-800 shadow-xs'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                <Smartphone className="w-3.5 h-3.5" />
                <span>Mobile SMS</span>
              </button>
            </div>
          )}

          {error && (
            <div className="mb-5 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs text-center font-bold">
              {error}
            </div>
          )}

          {!isOtpStep ? (
            authMode === 'email' ? (
              /* Email + 2-Step OTP Form */
              <form onSubmit={handleInitiateEmailLogin} className="space-y-4">
                <div>
                  <label className="block text-[11px] font-black text-slate-700 uppercase tracking-wider mb-1.5">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="pushkar.patade@example.com"
                      className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-cyan-600 font-medium"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] font-black text-slate-700 uppercase tracking-wider mb-1.5">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                    <input
                      type="password"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-cyan-600 font-medium"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSendingOtp || isLoading}
                  className="w-full mt-2 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-md disabled:opacity-50"
                >
                  {isSendingOtp ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      <span>Continue with Email OTP</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>

                <div className="relative flex py-2 items-center">
                  <div className="flex-grow border-t border-slate-200"></div>
                  <span className="flex-shrink mx-3 text-[11px] font-bold text-slate-400 uppercase tracking-wider">or 1-click</span>
                  <div className="flex-grow border-t border-slate-200"></div>
                </div>

                {/* 1-Click Firebase / Google Auto-Auth */}
                <button
                  type="button"
                  onClick={handleFirebaseLogin}
                  disabled={isLoading}
                  className="w-full py-2.5 px-4 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs flex items-center justify-center gap-2.5 transition-all shadow-xs"
                >
                  <Sparkles className="w-4 h-4 text-amber-500" />
                  <span>⚡ Continue with Firebase / Google Auto-Auth</span>
                </button>
              </form>
            ) : (
              /* Mobile Phone SMS Form */
              <form onSubmit={handleInitiatePhoneLogin} className="space-y-4">
                <div>
                  <label className="block text-[11px] font-black text-slate-700 uppercase tracking-wider mb-1.5">
                    Mobile Phone Number
                  </label>
                  <div className="relative">
                    <Phone className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                    <input
                      type="tel"
                      required
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      placeholder="+91 98765 43210"
                      className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-cyan-600 font-medium"
                    />
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">Include country code (e.g. +91 for India)</p>
                </div>

                <button
                  type="submit"
                  disabled={isSendingOtp || isLoading}
                  className="w-full mt-2 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-md disabled:opacity-50"
                >
                  {isSendingOtp ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      <span>Send Real SMS OTP via Firebase</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>

                <div className="relative flex py-2 items-center">
                  <div className="flex-grow border-t border-slate-200"></div>
                  <span className="flex-shrink mx-3 text-[11px] font-bold text-slate-400 uppercase tracking-wider">or 1-click</span>
                  <div className="flex-grow border-t border-slate-200"></div>
                </div>

                <button
                  type="button"
                  onClick={handleFirebaseLogin}
                  disabled={isLoading}
                  className="w-full py-2.5 px-4 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-bold text-xs flex items-center justify-center gap-2.5 transition-all shadow-xs"
                >
                  <Sparkles className="w-4 h-4 text-amber-500" />
                  <span>⚡ Continue with Firebase / Google Auto-Auth</span>
                </button>
              </form>
            )
          ) : (
            /* Step 2: 2-Step OTP Verification Form (Email or Phone SMS) */
            <form onSubmit={handleVerifyOtp} className="space-y-4">
              <div>
                <label className="block text-[11px] font-black text-slate-700 uppercase tracking-wider mb-1.5">
                  Enter 6-Digit {authMode === 'phone' ? 'SMS' : 'Email'} Code
                </label>
                <div className="relative">
                  <KeyRound className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                  <input
                    type="text"
                    required
                    maxLength={6}
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    placeholder="e.g. 848945"
                    className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-2.5 text-center text-lg font-mono tracking-widest text-slate-900 placeholder-slate-400 focus:outline-none focus:border-cyan-600 font-bold"
                  />
                </div>
              </div>

              {authMode === 'email' && demoOtp && (
                <div
                  onClick={() => setOtp(demoOtp)}
                  className="cursor-pointer p-2.5 rounded-xl bg-cyan-50 border border-cyan-200 text-cyan-800 text-xs flex items-center justify-between font-bold hover:bg-cyan-100 transition-all"
                >
                  <span className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-cyan-600" />
                    Dev Backup OTP: <code className="font-mono text-cyan-900 bg-white px-1.5 py-0.5 rounded border border-cyan-200">{demoOtp}</code>
                  </span>
                  <span className="text-[10px] text-cyan-700 underline">Tap to auto-fill</span>
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 rounded-xl bg-cyan-600 hover:bg-cyan-700 text-white font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-md disabled:opacity-50"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <span>Verify Code & Enter</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={() => setIsOtpStep(false)}
                className="w-full text-center text-xs text-slate-500 font-semibold hover:text-slate-800 transition-all pt-1"
              >
                ← Back
              </button>
            </form>
          )}

          <p className="text-center text-xs text-slate-500 font-medium mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-cyan-700 font-bold hover:underline">
              Create One
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};
