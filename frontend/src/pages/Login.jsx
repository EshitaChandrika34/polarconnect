import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff, Snowflake, XCircle } from "lucide-react";
import "./Login.css";
function Login() {
 const [showPassword, setShowPassword] = useState(false);
 const [view, setView] = useState("choice");
 const [role, setRole] = useState("Student");
 const [email, setEmail] = useState("");
 const [emailError, setEmailError] = useState("");
 const [password, setPassword] = useState("");
 const [passwordError, setPasswordError] = useState("");
  const navigate = useNavigate();

  if (view === "choice") {
    return (
      <div className="login-page">
        <div className="login-left">
          <div className="logo">
            <Snowflake size={32} />
            <span>PolarConnect</span>
          </div>

          <div className="left-content">
            <h1>
              From Polar Research
              <br />
              to Public Knowledge
            </h1>
            <p>
              Discover, understand and share knowledge from the Arctic and
              Antarctic regions.
            </p>
          </div>

          <div className="left-footer">
            PolarConnect • Polar Science Knowledge Portal
          </div>
        </div>

        <div className="login-right">
          <div className="login-box choice-box">
            <h2>Welcome to PolarConnect</h2>
            <p className="login-subtitle">Choose an option to get started.</p>

            <button className="login-button" type="button" onClick={() => setView("login")}>
              I already have an account
            </button>
            <button className="secondary-button" type="button" onClick={() => setView("register")}>
              Create an account
            </button>
          </div>
        </div>
      </div>
    );
  }

  const isRegistering = view === "register";

  return (
    <div className="login-page">

      <div className="login-left">

        <div className="logo">
          <Snowflake size={32} />
          <span>PolarConnect</span>
        </div>

        <div className="left-content">
          <h1>
            From Polar Research
            <br />
            to Public Knowledge
          </h1>

          <p>
            Discover, understand and share knowledge
            from the Arctic and Antarctic regions.
          </p>

          <div className="features">
            <div>❄️ Explore Polar Research</div>
            <div>📚 Access Scientific Knowledge</div>
            <div>🤖 AI Research Assistant</div>
          </div>
        </div>

        <div className="left-footer">
          PolarConnect • Polar Science Knowledge Portal
        </div>

      </div>

      <div className="login-right">

        <div className="login-box">

          <h2>{isRegistering ? "Create Your Account" : "Welcome Back"}</h2>

          <p className="login-subtitle">
            {isRegistering ? "Join the PolarConnect community" : "Login to access PolarConnect"}
          </p>

          <form
  onSubmit={(e) => {
    e.preventDefault();

    if (!/^[^\s@]+@gmail\.com$/i.test(email)) {
      setEmailError("Invalid email");
      setPasswordError("");
      return;
    }

    setEmailError("");

    if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*[^A-Za-z0-9\s]).{8,}$/.test(password)) {
      setPasswordError(
        "Password must be at least 8 characters and include an uppercase letter, a lowercase letter, and a special character."
      );
      return;
    }

    setPasswordError("");

    if (isRegistering) {
      setView("login");
    } else {
      const portalRoutes = {
        Student: "/student",
        Researcher: "/researcher",
      };

      navigate(portalRoutes[role] || "/public");
    }
  }}
>
            {isRegistering && (
              <div className="input-group">
                <label>Full Name</label>
                <input type="text" placeholder="Enter your full name" required />
              </div>
            )}

            <div className="input-group">
              <label>Email</label>

              <input
                type="text"
                inputMode="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setEmailError("");
                }}
                placeholder="Enter your Gmail address"
                aria-invalid={Boolean(emailError)}
                aria-describedby={emailError ? "email-error" : undefined}
                required
              />
              {emailError && <p className="field-error" id="email-error"><XCircle size={14} />{emailError}</p>}
            </div>

            <div className="input-group">
              <label>Password</label>

              <div className="password-input">

                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setPasswordError("");
                  }}
                  placeholder="Enter your password"
                  minLength={8}
                  aria-invalid={Boolean(passwordError)}
                  aria-describedby={passwordError ? "password-error" : undefined}
                  required
                />

                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff size={20} />
                  ) : (
                    <Eye size={20} />
                  )}
                </button>

              </div>
              {passwordError && <p className="field-error" id="password-error"><XCircle size={14} />{passwordError}</p>}
            </div>

            <div className="input-group">
              <label>Select Role</label>

              <select
  value={role}
  onChange={(e) => setRole(e.target.value)}
>
                <option>Student</option>
                <option>Researcher</option>
                <option>Public</option>
              </select>
            </div>

            <button className="login-button" type="submit">
              {isRegistering ? "Create Account" : "Login"}
            </button>

            <button className="back-button" type="button" onClick={() => setView("choice")}>
              Back to account options
            </button>

          </form>

        </div>

      </div>

    </div>
  );
}

export default Login;