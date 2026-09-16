// SA Modkit native client. C# 2.0 / .NET 2.0+
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
    TextBox pathBox, logBox;
    Label status, countLbl;
    Button installBtn;
    ArrayList packs, boxes;
    string kitRoot;
    bool busy;
    Color bg, panel, panel2, fg, muted, accent, warn, bad, green;

    public KitForm(string root) {
        kitRoot = root; packs = LoadPacks(root); boxes = new ArrayList();
        bg = Color.FromArgb(12,16,12); panel = Color.FromArgb(21,28,21); panel2 = Color.FromArgb(28,37,28);
        fg = Color.FromArgb(228,245,228); muted = Color.FromArgb(125,154,125);
        accent = Color.FromArgb(58,122,50); warn = Color.FromArgb(224,180,74);
        bad = Color.FromArgb(224,112,112); green = Color.FromArgb(198,255,122);
        Text = "SA Modkit"; Width = 920; Height = 640; MinimumSize = new Size(800, 560);
        BackColor = bg; ForeColor = fg; Font = new Font("Segoe UI", 9);
        StartPosition = FormStartPosition.CenterScreen;

        Panel header = new Panel(); header.Dock = DockStyle.Top; header.Height = 64; header.BackColor = bg;
        Label title = new Label(); title.Text = "SA MODKIT"; title.Font = new Font("Segoe UI", 18, FontStyle.Bold);
        title.ForeColor = green; title.AutoSize = true; title.Location = new Point(16, 8); header.Controls.Add(title);
        Label hint = new Label(); hint.Text = "Windows 7 - 11    tick packs    nothing else is copied";
        hint.ForeColor = muted; hint.AutoSize = true; hint.Location = new Point(18, 38); header.Controls.Add(hint);

        Panel dest = new Panel(); dest.Dock = DockStyle.Top; dest.Height = 96; dest.BackColor = panel;
        Label destCap = new Label(); destCap.Text = "GAME FOLDER"; destCap.ForeColor = muted; destCap.AutoSize = true;
        destCap.Location = new Point(16, 8); dest.Controls.Add(destCap);
        pathBox = new TextBox(); pathBox.Location = new Point(16, 28); pathBox.Width = 760;
        pathBox.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
        pathBox.BackColor = Color.FromArgb(10,14,10); pathBox.ForeColor = fg;
        pathBox.BorderStyle = BorderStyle.FixedSingle; pathBox.Text = GuessGta(root); dest.Controls.Add(pathBox);
        Button browse = MkBtn("Browse...", 0, 0);
        browse.Anchor = AnchorStyles.Top | AnchorStyles.Right; browse.Location = new Point(784, 26);
        browse.Click += new EventHandler(OnBrowse); dest.Controls.Add(browse);
        status = new Label(); status.Location = new Point(16, 56); status.AutoSize = true; status.ForeColor = green;
        dest.Controls.Add(status);

        Panel footer = new Panel(); footer.Dock = DockStyle.Bottom; footer.Height = 52; footer.BackColor = bg;
        installBtn = MkBtn("Install selected", 16, 12); installBtn.Width = 140;
        installBtn.Click += new EventHandler(OnInstall); footer.Controls.Add(installBtn);
        Button none = MkBtn("None", 164, 12); none.Click += new EventHandler(OnNone); footer.Controls.Add(none);
        Button ready = MkBtn("Ready", 258, 12); ready.Click += new EventHandler(OnReady); footer.Controls.Add(ready);
        Button verify = MkBtn("Verify", 352, 12); verify.Click += new EventHandler(OnVerify); footer.Controls.Add(verify);
        countLbl = new Label(); countLbl.Text = "0 selected"; countLbl.ForeColor = muted; countLbl.AutoSize = true;
        countLbl.Anchor = AnchorStyles.Top | AnchorStyles.Right; countLbl.Location = new Point(800, 18);
        footer.Controls.Add(countLbl);

        SplitContainer split = new SplitContainer(); split.Dock = DockStyle.Fill; split.BackColor = bg;
        split.SplitterDistance = 500; split.SplitterWidth = 8;
        Panel packHost = new Panel(); packHost.Dock = DockStyle.Fill; packHost.BackColor = panel;
        Label packCap = new Label(); packCap.Text = "PACKS"; packCap.ForeColor = muted; packCap.Dock = DockStyle.Top; packCap.Height = 24;
        Panel scroller = new Panel(); scroller.Dock = DockStyle.Fill; scroller.AutoScroll = true; scroller.BackColor = panel;
        packHost.Controls.Add(scroller); packHost.Controls.Add(packCap);
        int y = 8;
        for (int i = 0; i < packs.Count; i++) {
            Pack p = (Pack)packs[i];
            Panel card = new Panel(); card.Location = new Point(10, y); card.Size = new Size(460, 58);
            card.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right; card.BackColor = panel2;
            Panel stripe = new Panel(); stripe.Dock = DockStyle.Left; stripe.Width = 4;
            stripe.BackColor = p.Ready ? green : bad; card.Controls.Add(stripe);
            CheckBox cb = new CheckBox(); cb.Location = new Point(14, 6); cb.Width = 430;
            cb.FlatStyle = FlatStyle.Flat; cb.BackColor = panel2; cb.ForeColor = p.Ready ? fg : muted;
            cb.Text = p.Ready ? p.Name : (p.Name + "  --  " + p.Reason);
            cb.Enabled = p.Ready; cb.Checked = false; cb.Tag = p;
            cb.CheckedChanged += new EventHandler(OnToggle);
            card.Controls.Add(cb); boxes.Add(cb);
            Label bl = new Label(); bl.Location = new Point(32, 30); bl.Width = 410;
            bl.ForeColor = muted; bl.BackColor = panel2; bl.Text = p.Blurb == null ? "" : p.Blurb;
            card.Controls.Add(bl); scroller.Controls.Add(card); y += 66;
        }
        Panel logHost = new Panel(); logHost.Dock = DockStyle.Fill; logHost.BackColor = panel;
        Label logCap = new Label(); logCap.Text = "LOG"; logCap.ForeColor = muted; logCap.Dock = DockStyle.Top; logCap.Height = 24;
        logBox = new TextBox(); logBox.Multiline = true; logBox.ScrollBars = ScrollBars.Vertical; logBox.ReadOnly = true;
        logBox.Dock = DockStyle.Fill; logBox.BackColor = Color.FromArgb(10,14,10); logBox.ForeColor = fg; logBox.BorderStyle = BorderStyle.None;
        logHost.Controls.Add(logBox); logHost.Controls.Add(logCap);
        split.Panel1.Controls.Add(packHost); split.Panel2.Controls.Add(logHost);
        Controls.Add(split); Controls.Add(dest); Controls.Add(header); Controls.Add(footer);
        RefreshDetect(); UpdateCount(); Log("SA-Modkit.exe"); Log("Tick packs, then Install selected.");
    }

    Button MkBtn(string text, int x, int y) {
        Button b = new Button(); b.Text = text; b.Location = new Point(x, y); b.Width = 88; b.Height = 28;
        b.BackColor = accent; b.ForeColor = green; b.FlatStyle = FlatStyle.Flat;
        b.FlatAppearance.BorderSize = 0; b.Cursor = Cursors.Hand; return b;
    }
    void UpdateCount() { countLbl.Text = Selected().Count.ToString() + " selected"; }
    void OnToggle(object sender, EventArgs e) {
        CheckBox a = sender as CheckBox;
        if (a != null && a.Checked) {
            Pack p = a.Tag as Pack;
            if (p != null) {
                if (p.Id == "switcher-full") UncheckId("switcher-skin");
                if (p.Id == "switcher-skin") UncheckId("switcher-full");
            }
        }
        UpdateCount();
    }
    void UncheckId(string id) {
        for (int i = 0; i < boxes.Count; i++) {
            CheckBox cb = (CheckBox)boxes[i]; Pack p = cb.Tag as Pack;
            if (p != null && p.Id == id) cb.Checked = false;
        }
    }
    void OnNone(object sender, EventArgs e) {
        for (int i = 0; i < boxes.Count; i++) ((CheckBox)boxes[i]).Checked = false; UpdateCount();
    }
    void OnReady(object sender, EventArgs e) {
        for (int i = 0; i < boxes.Count; i++) {
            CheckBox cb = (CheckBox)boxes[i]; Pack p = cb.Tag as Pack;
            cb.Checked = p != null && p.Ready;
        }
        UncheckId("switcher-skin"); UpdateCount();
    }
    void OnBrowse(object sender, EventArgs e) {
        FolderBrowserDialog d = new FolderBrowserDialog();
        d.Description = "Folder that contains gta_sa.exe";
        if (d.ShowDialog() == DialogResult.OK) { pathBox.Text = d.SelectedPath; RefreshDetect(); }
    }
    void RefreshDetect() {
        string gta = pathBox.Text.Trim(); string exe = Path.Combine(gta, "gta_sa.exe");
        if (!File.Exists(exe)) { status.Text = "No gta_sa.exe in that folder"; status.ForeColor = bad; return; }
        long size = 0; try { size = new FileInfo(exe).Length; } catch {}
        string kind = "unknown build";
        if (size >= 13000000 && size <= 16000000) kind = "likely 1.0";
        else if (size > 20000000) kind = "likely Steam 3.0 — downgrade";
        bool cleo = File.Exists(Path.Combine(gta, "CLEO.asi"));
        bool sp = File.Exists(Path.Combine(gta, "SilentPatchSA.asi"));
        string sanny = FindSanny();
        status.Text = kind + "   |   CLEO " + (cleo ? "yes" : "NO") + "   |   SilentPatch " + (sp ? "yes" : "no") + "   |   Sanny " + (sanny.Length > 0 ? "yes" : "NO");
        if (!cleo || kind.IndexOf("3.0") >= 0) status.ForeColor = warn; else status.ForeColor = green;
        SaveText(Path.Combine(kitRoot, "GTA_DIR.txt"), gta);
    }
    void OnInstall(object sender, EventArgs e) {
        if (busy) return;
        string gta = pathBox.Text.Trim();
        if (!File.Exists(Path.Combine(gta, "gta_sa.exe"))) { MessageBox.Show(this, "Pick the folder that contains gta_sa.exe.", "SA Modkit"); return; }
        ArrayList ids = Selected();
        if (ids.Count == 0) { MessageBox.Show(this, "No packs ticked.", "SA Modkit"); return; }
        string list = ""; for (int i = 0; i < ids.Count; i++) { if (i > 0) list += "\n"; list += (string)ids[i]; }
        if (MessageBox.Show(this, "Install only these?\n\n" + list, "SA Modkit", MessageBoxButtons.YesNo) != DialogResult.Yes) return;
        busy = true; installBtn.Enabled = false; installBtn.Text = "Installing...";
        try { Install(gta, ids); }
        finally { busy = false; installBtn.Enabled = true; installBtn.Text = "Install selected"; RefreshDetect(); UpdateCount(); }
    }
    void OnVerify(object sender, EventArgs e) {
        string gta = pathBox.Text.Trim();
        string[] names = new string[] { "CLEO\\GroveLinkPhone.cs", "CLEO\\MissionSwitcher.cs", "CLEO\\AW_FPS_Core.cs", "CLEO\\GroveCast.cs" };
        for (int i = 0; i < names.Length; i++) {
            string p = Path.Combine(gta, names[i]);
            if (File.Exists(p)) Log("ok   " + names[i] + "  (" + new FileInfo(p).Length + ")"); else Log("miss " + names[i]);
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
        Directory.CreateDirectory(Path.Combine(gta, "CLEO")); Directory.CreateDirectory(Path.Combine(gta, "CLEO\\GroveLink"));
        string sanny = FindSanny();
        if (sanny.Length == 0) Log("Sanny not found — copying .txt next to dest"); else Log("Sanny  " + sanny);
        Pack full = ById("switcher-full");
        if (ids.Contains("switcher-full") && full != null && full.Ready) {
            ArrayList slim = new ArrayList();
            for (int i = 0; i < ids.Count; i++) if ((string)ids[i] != "switcher-skin") slim.Add(ids[i]);
            ids = slim; Log("using  full companion switcher");
        }
        for (int i = 0; i < ids.Count; i++) {
            Pack p = ById((string)ids[i]); if (p == null) continue;
            Log("----  " + p.Name); Application.DoEvents();
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
                Log("sanny  " + Path.GetFileName(src)); Application.DoEvents();
                try {
                    ProcessStartInfo psi = new ProcessStartInfo();
                    psi.FileName = sanny; psi.Arguments = "--compile \"" + src + "\" \"" + dest + "\"";
                    psi.UseShellExecute = false; psi.CreateNoWindow = true;
                    Process pr = Process.Start(psi); pr.WaitForExit();
                } catch (Exception ex) { Log("FAIL  " + ex.Message); }
                if (File.Exists(dest)) Log("ok    " + dest); else Log("FAIL  no output " + dest);
            }
        }
        SaveText(Path.Combine(gta, "CLEO\\GroveLink\\modkit.txt"), "sa-modkit exe\n");
        Log("done"); MessageBox.Show(this, "Install finished. Check the log.", "SA Modkit");
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
        for (int i = 0; i < common.Length; i++) if (File.Exists(common[i])) return common[i]; return "";
    }
    static string ReadText(string path) {
        try { StreamReader sr = new StreamReader(path); string t = sr.ReadToEnd().Trim(); sr.Close(); return t; } catch { return ""; }
    }
    static void SaveText(string path, string text) {
        try { string dir = Path.GetDirectoryName(path); if (dir != null && dir.Length > 0) Directory.CreateDirectory(dir);
            StreamWriter sw = new StreamWriter(path); sw.Write(text); if (!text.EndsWith("\n")) sw.Write("\n"); sw.Close(); } catch {}
    }
    static string ResolveRoot(string kit, Hashtable kv) {
        string local = kv["root_local"] as string;
        if (local != null && local.Length > 0) {
            string p = Path.Combine(kit, local.Replace('/', Path.DirectorySeparatorChar)); if (Directory.Exists(p)) return p;
        }
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
        sr.Close(); if (cur != null) { cur.Root = ResolveRoot(kit, kv); FinishReady(cur); list.Add(cur); } return list;
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
