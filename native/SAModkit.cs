// SA Modkit native client. C# 2.0 / .NET 2.0+
// BUILD_EXE.bat -> SA-Modkit.exe
using System;
using System.Collections;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Windows.Forms;

public class Pack {
    public string Id, Name, Blurb, Root, Reason;
    public ArrayList Files, Compile;
    public int MinBytes;
    public bool Ready;
}

public class KitForm : Form {
    TextBox pathBox, logBox; Label status; ArrayList packs, boxes; string kitRoot; bool busy;
    public KitForm(string root) {
        kitRoot = root; packs = LoadPacks(root); boxes = new ArrayList();
        Text = "SA Modkit"; Width = 780; Height = 560; MinimumSize = new Size(700, 500);
        BackColor = Color.FromArgb(16,20,16); ForeColor = Color.FromArgb(216,245,216);
        Font = new Font("Segoe UI", 9);
        Label title = new Label(); title.Text = "SA MODKIT"; title.Font = new Font("Segoe UI", 16, FontStyle.Bold);
        title.ForeColor = Color.FromArgb(182,255,107); title.AutoSize = true; title.Location = new Point(16,12); Controls.Add(title);
        Label hint = new Label(); hint.Text = "Tick only the packs you want. Unticked packs stay off the game.";
        hint.AutoSize = true; hint.ForeColor = Color.FromArgb(122,154,122); hint.Location = new Point(16,44); Controls.Add(hint);
        Label dest = new Label(); dest.Text = "GTA San Andreas folder"; dest.AutoSize = true; dest.Location = new Point(16,74);
        dest.ForeColor = Color.FromArgb(122,154,122); Controls.Add(dest);
        pathBox = new TextBox(); pathBox.Location = new Point(16,94); pathBox.Width = 620;
        pathBox.Anchor = AnchorStyles.Top|AnchorStyles.Left|AnchorStyles.Right; pathBox.Text = GuessGta(root); Controls.Add(pathBox);
        Button browse = MkBtn("Browse...", 646, 92); browse.Click += new EventHandler(OnBrowse);
        browse.Anchor = AnchorStyles.Top|AnchorStyles.Right; Controls.Add(browse);
        status = new Label(); status.Location = new Point(16,122); status.AutoSize = true;
        status.ForeColor = Color.FromArgb(182,255,107); Controls.Add(status);
        int y = 150;
        for (int i = 0; i < packs.Count; i++) {
            Pack p = (Pack)packs[i];
            CheckBox cb = new CheckBox(); cb.Location = new Point(20,y); cb.Width = 420;
            cb.ForeColor = p.Ready ? ForeColor : Color.Gray;
            cb.Text = p.Ready ? p.Name : (p.Name + "  --  " + p.Reason);
            cb.Enabled = p.Ready; cb.Checked = false; cb.Tag = p;
            cb.CheckedChanged += new EventHandler(OnToggle); Controls.Add(cb); boxes.Add(cb); y += 22;
            Label bl = new Label(); bl.Text = "    " + p.Blurb; bl.ForeColor = Color.FromArgb(122,154,122);
            bl.Location = new Point(36,y); bl.AutoSize = true; Controls.Add(bl); y += 20;
        }
        Button none = MkBtn("None", 16, y+8); none.Click += new EventHandler(OnNone); Controls.Add(none);
        Button ready = MkBtn("Ready", 110, y+8); ready.Click += new EventHandler(OnReady); Controls.Add(ready);
        Button install = MkBtn("Install selected", 204, y+8); install.Width = 130; install.Click += new EventHandler(OnInstall); Controls.Add(install);
        Button verify = MkBtn("Verify", 344, y+8); verify.Click += new EventHandler(OnVerify); Controls.Add(verify);
        logBox = new TextBox(); logBox.Multiline = true; logBox.ScrollBars = ScrollBars.Vertical; logBox.ReadOnly = true;
        logBox.BackColor = Color.FromArgb(13,18,13); logBox.ForeColor = ForeColor;
        logBox.Location = new Point(460,150); logBox.Size = new Size(290, y-150+40);
        logBox.Anchor = AnchorStyles.Top|AnchorStyles.Bottom|AnchorStyles.Right; Controls.Add(logBox);
        RefreshDetect(); Log("SA-Modkit.exe  —  no Python needed."); Log("Tick packs, then Install selected.");
    }
    Button MkBtn(string text, int x, int y) {
        Button b = new Button(); b.Text = text; b.Location = new Point(x,y); b.Width = 88; b.Height = 26;
        b.BackColor = Color.FromArgb(47,93,47); b.ForeColor = Color.FromArgb(182,255,107); b.FlatStyle = FlatStyle.Flat; return b;
    }
    void OnToggle(object sender, EventArgs e) {
        CheckBox a = sender as CheckBox; if (a == null || !a.Checked) return;
        Pack p = a.Tag as Pack; if (p == null) return;
        if (p.Id == "switcher-full") UncheckId("switcher-skin");
        if (p.Id == "switcher-skin") UncheckId("switcher-full");
    }
    void UncheckId(string id) {
        for (int i = 0; i < boxes.Count; i++) {
            CheckBox cb = (CheckBox)boxes[i]; Pack p = cb.Tag as Pack;
            if (p != null && p.Id == id) cb.Checked = false;
        }
    }
    void OnNone(object sender, EventArgs e) { for (int i = 0; i < boxes.Count; i++) ((CheckBox)boxes[i]).Checked = false; }
    void OnReady(object sender, EventArgs e) {
        for (int i = 0; i < boxes.Count; i++) {
            CheckBox cb = (CheckBox)boxes[i]; Pack p = cb.Tag as Pack;
            cb.Checked = p != null && p.Ready;
        }
        UncheckId("switcher-skin");
    }
    void OnBrowse(object sender, EventArgs e) {
        FolderBrowserDialog d = new FolderBrowserDialog();
        d.Description = "Folder that contains gta_sa.exe";
        if (d.ShowDialog() == DialogResult.OK) { pathBox.Text = d.SelectedPath; RefreshDetect(); }
    }
    void RefreshDetect() {
        string gta = pathBox.Text.Trim(); string exe = Path.Combine(gta, "gta_sa.exe");
        if (!File.Exists(exe)) { status.Text = "No game selected"; return; }
        long size = 0; try { size = new FileInfo(exe).Length; } catch {}
        string kind = "unknown build";
        if (size >= 13000000 && size <= 16000000) kind = "likely 1.0";
        else if (size > 20000000) kind = "likely Steam 3.0 — downgrade";
        bool cleo = File.Exists(Path.Combine(gta, "CLEO.asi"));
        bool sp = File.Exists(Path.Combine(gta, "SilentPatchSA.asi"));
        string sanny = FindSanny();
        status.Text = kind + "  |  CLEO " + (cleo?"yes":"NO") + "  |  SilentPatch " + (sp?"yes":"no") + "  |  Sanny " + (sanny.Length>0?"yes":"NO");
        SaveText(Path.Combine(kitRoot, "GTA_DIR.txt"), gta);
    }
    void OnInstall(object sender, EventArgs e) {
        if (busy) return;
        string gta = pathBox.Text.Trim();
        if (!File.Exists(Path.Combine(gta, "gta_sa.exe"))) { MessageBox.Show("Pick the folder that contains gta_sa.exe."); return; }
        ArrayList ids = Selected();
        if (ids.Count == 0) { MessageBox.Show("No packs ticked."); return; }
        string list = ""; for (int i = 0; i < ids.Count; i++) { if (i>0) list += "\n"; list += (string)ids[i]; }
        if (MessageBox.Show("Install only these?\n\n"+list, "SA Modkit", MessageBoxButtons.YesNo) != DialogResult.Yes) return;
        busy = true; try { Install(gta, ids); } finally { busy = false; RefreshDetect(); }
    }
    void OnVerify(object sender, EventArgs e) {
        string gta = pathBox.Text.Trim();
        string[] names = new string[] { "CLEO\\GroveLinkPhone.cs", "CLEO\\MissionSwitcher.cs", "CLEO\\AW_FPS_Core.cs", "CLEO\\GroveCast.cs" };
        for (int i = 0; i < names.Length; i++) {
            string p = Path.Combine(gta, names[i]);
            if (File.Exists(p)) Log("ok  " + names[i] + "  (" + new FileInfo(p).Length + ")");
            else Log("miss  " + names[i]);
        }
    }
    ArrayList Selected() {
        ArrayList ids = new ArrayList();
        for (int i = 0; i < boxes.Count; i++) {
            CheckBox cb = (CheckBox)boxes[i]; Pack p = cb.Tag as Pack;
            if (cb.Checked && p != null && p.Ready) ids.Add(p.Id);
        }
        return ids;
    }
    Pack ById(string id) { for (int i = 0; i < packs.Count; i++) { Pack p = (Pack)packs[i]; if (p.Id == id) return p; } return null; }
    void Install(string gta, ArrayList ids) {
        Directory.CreateDirectory(Path.Combine(gta, "CLEO"));
        Directory.CreateDirectory(Path.Combine(gta, "CLEO\\GroveLink"));
        string sanny = FindSanny();
        if (sanny.Length == 0) Log("Sanny not found — copying .txt next to dest"); else Log("Sanny  " + sanny);
        Pack full = ById("switcher-full");
        if (ids.Contains("switcher-full") && full != null && full.Ready) {
            ArrayList slim = new ArrayList();
            for (int i = 0; i < ids.Count; i++) if ((string)ids[i] != "switcher-skin") slim.Add(ids[i]);
            ids = slim; Log("using  full companion switcher");
        }
        for (int i = 0; i < ids.Count; i++) {
            Pack p = ById((string)ids[i]); if (p == null) continue; Log("----  " + p.Name);
            for (int f = 0; f < p.Files.Count; f++) {
                string[] row = (string[])p.Files[f];
                string src = Path.Combine(p.Root, row[0].Replace('/', Path.DirectorySeparatorChar));
                string dest = Path.Combine(gta, row[1].Replace('/', Path.DirectorySeparatorChar));
                if (row[2] == "1" && File.Exists(dest)) { Log("keep  " + dest); continue; }
                CopyOne(src, dest);
            }
            for (int c = 0; c < p.Compile.Count; c++) {
                string[] row = (string[])p.Compile[c];
                string src = Path.Combine(p.Root, row[0].Replace('/', Path.DirectorySeparatorChar));
                string dest = Path.Combine(gta, row[1].Replace('/', Path.DirectorySeparatorChar));
                if (p.MinBytes > 0 && File.Exists(src) && new FileInfo(src).Length < p.MinBytes) { Log("skip stub  " + row[0]); continue; }
                if (sanny.Length == 0) { CopyOne(src, dest + ".txt"); continue; }
                Directory.CreateDirectory(Path.GetDirectoryName(dest));
                Log("sanny  " + Path.GetFileName(src));
                try {
                    ProcessStartInfo psi = new ProcessStartInfo();
                    psi.FileName = sanny; psi.Arguments = "--compile \"" + src + "\" \"" + dest + "\"";
                    psi.UseShellExecute = false; psi.CreateNoWindow = true;
                    Process pr = Process.Start(psi); pr.WaitForExit();
                } catch (Exception ex) { Log("FAIL  " + ex.Message); }
                if (File.Exists(dest)) Log("ok  " + dest); else Log("FAIL  no output " + dest);
            }
        }
        SaveText(Path.Combine(gta, "CLEO\\GroveLink\\modkit.txt"), "sa-modkit exe\n");
        Log("done"); MessageBox.Show("Install finished. Check the log.");
    }
    void CopyOne(string src, string dest) {
        try { Directory.CreateDirectory(Path.GetDirectoryName(dest)); File.Copy(src, dest, true); Log("copy  " + dest); }
        catch (Exception ex) { Log("FAIL  " + src + "  " + ex.Message); }
    }
    void Log(string s) { logBox.AppendText(s + "\r\n"); }
    static string GuessGta(string kit) {
        string remembered = Path.Combine(kit, "GTA_DIR.txt");
        if (File.Exists(remembered)) { string t = ReadText(remembered); if (File.Exists(Path.Combine(t, "gta_sa.exe"))) return t; }
        string[] common = new string[] { @"C:\GTA San Andreas", @"D:\GTA San Andreas", @"E:\GTA San Andreas",
            @"C:\Program Files (x86)\Rockstar Games\GTA San Andreas", @"C:\Program Files\Rockstar Games\GTA San Andreas",
            @"C:\Program Files (x86)\Steam\steamapps\common\Grand Theft Auto San Andreas" };
        for (int i = 0; i < common.Length; i++) if (File.Exists(Path.Combine(common[i], "gta_sa.exe"))) return common[i];
        return "";
    }
    static string FindSanny() {
        string[] common = new string[] {
            @"C:\Program Files\Sanny Builder 4\sanny.exe", @"C:\Program Files\Sanny Builder 3\sanny.exe",
            @"C:\Program Files (x86)\Sanny Builder 4\sanny.exe", @"C:\Program Files (x86)\Sanny Builder 3\sanny.exe",
            @"C:\Sanny Builder 4\sanny.exe", @"C:\Sanny Builder 3\sanny.exe" };
        for (int i = 0; i < common.Length; i++) if (File.Exists(common[i])) return common[i];
        return "";
    }
    static string ReadText(string path) { try { StreamReader sr = new StreamReader(path); string t = sr.ReadToEnd().Trim(); sr.Close(); return t; } catch { return ""; } }
    static void SaveText(string path, string text) {
        try { string dir = Path.GetDirectoryName(path); if (dir != null && dir.Length > 0) Directory.CreateDirectory(dir);
            StreamWriter sw = new StreamWriter(path); sw.Write(text); if (!text.EndsWith("\n")) sw.Write("\n"); sw.Close(); } catch {}
    }
    static string ResolveRoot(string kit, Hashtable kv) {
        string local = kv["root_local"] as string;
        if (local != null && local.Length > 0) { string p = Path.Combine(kit, local.Replace('/', Path.DirectorySeparatorChar)); if (Directory.Exists(p)) return p; }
        string sib = kv["root_sibling"] as string;
        if (sib != null && sib.Length > 0) {
            string parent = Directory.GetParent(kit).FullName;
            string p = Path.Combine(parent, sib); if (Directory.Exists(p)) return p;
            p = Path.Combine(kit, "vendor\\" + sib); if (Directory.Exists(p)) return p;
            p = Path.Combine(kit, "packs\\" + sib); if (Directory.Exists(p)) return p;
        }
        return "";
    }
    static ArrayList LoadPacks(string kit) {
        ArrayList list = new ArrayList(); string ini = Path.Combine(kit, "packs.ini"); if (!File.Exists(ini)) return list;
        StreamReader sr = new StreamReader(ini); string line; Pack cur = null; Hashtable kv = new Hashtable();
        while ((line = sr.ReadLine()) != null) {
            line = line.Trim();
            if (line.Length == 0 || line.StartsWith(";") || line.StartsWith("#")) continue;
            if (line.StartsWith("[") && line.EndsWith("]")) {
                if (cur != null) { cur.Root = ResolveRoot(kit, kv); FinishReady(cur); list.Add(cur); }
                cur = new Pack(); cur.Id = line.Substring(1, line.Length-2); cur.Name = cur.Id; cur.Blurb = "";
                cur.Files = new ArrayList(); cur.Compile = new ArrayList(); kv = new Hashtable(); continue;
            }
            if (cur == null || line.IndexOf('=') < 0) continue;
            int eq = line.IndexOf('='); string key = line.Substring(0, eq).Trim(); string val = line.Substring(eq+1).Trim();
            if (key == "name") cur.Name = val;
            else if (key == "blurb") cur.Blurb = val;
            else if (key == "min_source_bytes") { try { cur.MinBytes = int.Parse(val); } catch {} }
            else if (key == "file") { string[] parts = val.Split('|'); if (parts.Length >= 2) cur.Files.Add(new string[] { parts[0], parts[1], parts.Length>2?parts[2]:"0" }); }
            else if (key == "compile") { string[] parts = val.Split('|'); if (parts.Length >= 2) cur.Compile.Add(new string[] { parts[0], parts[1] }); }
            else kv[key] = val;
        }
        sr.Close();
        if (cur != null) { cur.Root = ResolveRoot(kit, kv); FinishReady(cur); list.Add(cur); }
        return list;
    }
    static void FinishReady(Pack p) {
        if (p.Root == null || p.Root.Length == 0) { p.Ready = false; p.Reason = "clone missing"; return; }
        for (int i = 0; i < p.Compile.Count; i++) {
            string[] row = (string[])p.Compile[i];
            string src = Path.Combine(p.Root, row[0].Replace('/', Path.DirectorySeparatorChar));
            if (!File.Exists(src)) { p.Ready = false; p.Reason = "missing " + row[0]; return; }
            if (p.MinBytes > 0 && new FileInfo(src).Length < p.MinBytes) { p.Ready = false; p.Reason = "stub source"; return; }
        }
        for (int i = 0; i < p.Files.Count; i++) {
            string[] row = (string[])p.Files[i];
            string src = Path.Combine(p.Root, row[0].Replace('/', Path.DirectorySeparatorChar));
            if (!File.Exists(src)) { p.Ready = false; p.Reason = "missing " + row[0]; return; }
        }
        p.Ready = true; p.Reason = "ready";
    }
    [STAThread] public static void Main() {
        string root = AppDomain.CurrentDomain.BaseDirectory.TrimEnd('\\','/');
        Application.EnableVisualStyles(); Application.Run(new KitForm(root));
    }
}
