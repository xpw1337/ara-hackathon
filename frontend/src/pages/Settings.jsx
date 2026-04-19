import { useState } from "react";
import { Save, Check, AlertCircle } from "lucide-react";

export default function Settings() {
  const [settings, setSettings] = useState({
    keywords: "machine learning, computer vision, neural networks",
    repoName: "pitch-tipping",
    deliveryChannel: "telegram",
    writeDestination: "notion",
    canvasUrl: "https://canvas.jhu.edu",
    canvasToken: "",
  });
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    console.log("Saving settings:", settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* Header */}
      <div className="card-brutal bg-brutal-purple">
        <h1 className="text-3xl font-bold">⚙️ Settings</h1>
        <p className="font-mono mt-2">
          Configure your integrations and preferences
        </p>
      </div>

      {/* Research Keywords */}
      <div className="card-brutal">
        <h2 className="font-bold text-xl mb-4 flex items-center gap-2">
          📚 Research Keywords
        </h2>
        <p className="text-sm font-mono mb-3 opacity-70">
          Comma-separated keywords for paper discovery
        </p>
        <textarea
          value={settings.keywords}
          onChange={(e) =>
            setSettings({ ...settings, keywords: e.target.value })
          }
          className="input-brutal min-h-[100px] resize-none"
          placeholder="machine learning, transformers, attention..."
        />
      </div>

      {/* Project Settings */}
      <div className="card-brutal">
        <h2 className="font-bold text-xl mb-4">🔧 Project Settings</h2>

        <div className="space-y-4">
          <div>
            <label className="block font-bold mb-2">GitHub Repo Name</label>
            <input
              type="text"
              value={settings.repoName}
              onChange={(e) =>
                setSettings({ ...settings, repoName: e.target.value })
              }
              className="input-brutal"
              placeholder="my-research-project"
            />
          </div>
        </div>
      </div>

      {/* Delivery Preferences */}
      <div className="card-brutal">
        <h2 className="font-bold text-xl mb-4">📬 Delivery Preferences</h2>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block font-bold mb-2">Nudge Channel</label>
            <div className="space-y-2">
              {["telegram", "whatsapp"].map((channel) => (
                <label
                  key={channel}
                  className={`flex items-center gap-3 p-3 border-3 border-brutal-black cursor-pointer
                    ${
                      settings.deliveryChannel === channel
                        ? "bg-brutal-lime"
                        : "bg-brutal-white hover:bg-gray-100"
                    }`}
                >
                  <input
                    type="radio"
                    name="deliveryChannel"
                    value={channel}
                    checked={settings.deliveryChannel === channel}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        deliveryChannel: e.target.value,
                      })
                    }
                    className="w-5 h-5"
                  />
                  <span className="font-bold capitalize">{channel}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block font-bold mb-2">Write Destination</label>
            <div className="space-y-2">
              {["notion", "google-drive"].map((dest) => (
                <label
                  key={dest}
                  className={`flex items-center gap-3 p-3 border-3 border-brutal-black cursor-pointer
                    ${
                      settings.writeDestination === dest
                        ? "bg-brutal-lime"
                        : "bg-brutal-white hover:bg-gray-100"
                    }`}
                >
                  <input
                    type="radio"
                    name="writeDestination"
                    value={dest}
                    checked={settings.writeDestination === dest}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        writeDestination: e.target.value,
                      })
                    }
                    className="w-5 h-5"
                  />
                  <span className="font-bold capitalize">
                    {dest.replace("-", " ")}
                  </span>
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Canvas Integration */}
      <div className="card-brutal bg-brutal-coral">
        <h2 className="font-bold text-xl mb-4 flex items-center gap-2">
          🎓 Canvas Integration
          <span className="tag-brutal bg-brutal-white text-sm">Required</span>
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block font-bold mb-2">Canvas Base URL</label>
            <input
              type="url"
              value={settings.canvasUrl}
              onChange={(e) =>
                setSettings({ ...settings, canvasUrl: e.target.value })
              }
              className="input-brutal"
              placeholder="https://canvas.university.edu"
            />
          </div>

          <div>
            <label className="block font-bold mb-2">Canvas API Token</label>
            <input
              type="password"
              value={settings.canvasToken}
              onChange={(e) =>
                setSettings({ ...settings, canvasToken: e.target.value })
              }
              className="input-brutal"
              placeholder="••••••••••••••••"
            />
            <p className="text-sm font-mono mt-2 flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              Get this from Canvas → Account → Settings → New Access Token
            </p>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <button
        onClick={handleSave}
        className={`btn-brutal w-full flex items-center justify-center gap-2 text-lg
          ${saved ? "bg-brutal-mint text-brutal-black" : ""}`}
      >
        {saved ? (
          <>
            <Check className="w-6 h-6" />
            Saved!
          </>
        ) : (
          <>
            <Save className="w-6 h-6" />
            Save Settings
          </>
        )}
      </button>
    </div>
  );
}