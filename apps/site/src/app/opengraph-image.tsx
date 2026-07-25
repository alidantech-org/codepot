import { ImageResponse } from "next/og";

export const alt = "Codepot African code pot mark and developer tooling platform";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          position: "relative",
          overflow: "hidden",
          background: "linear-gradient(135deg, #1b100a 0%, #3a2013 55%, #1e110a 100%)",
          color: "#fff7ed",
          padding: "72px",
          fontFamily: "Arial, sans-serif",
        }}
      >
        <div
          style={{
            position: "absolute",
            width: "460px",
            height: "460px",
            borderRadius: "999px",
            right: "-80px",
            top: "-70px",
            background: "radial-gradient(circle, rgba(218,154,88,.34), rgba(218,154,88,0) 70%)",
          }}
        />
        <div
          style={{
            position: "absolute",
            width: "300px",
            height: "300px",
            borderRadius: "999px",
            left: "350px",
            bottom: "-190px",
            background: "radial-gradient(circle, rgba(224,179,110,.2), rgba(224,179,110,0) 70%)",
          }}
        />

        <div style={{ display: "flex", flexDirection: "column", width: "64%", justifyContent: "center", zIndex: 2 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "18px", marginBottom: "34px" }}>
            <div
              style={{
                width: "64px",
                height: "64px",
                borderRadius: "18px",
                background: "#a85e2e",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "27px",
                fontWeight: 700,
                color: "#fff7ed",
                transform: "rotate(-8deg)",
              }}
            >
              {"</>"}
            </div>
            <div style={{ display: "flex", fontSize: "34px", fontWeight: 700, letterSpacing: "-1px" }}>Codepot</div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", fontSize: "68px", lineHeight: 1.02, fontWeight: 700, letterSpacing: "-3px", maxWidth: "720px" }}>
            <span>Typed software intent,</span>
            <span style={{ color: "#e0b36e" }}>crafted to flow.</span>
          </div>
          <div style={{ display: "flex", marginTop: "28px", fontSize: "25px", lineHeight: 1.45, color: "#d8c4b0", maxWidth: "700px" }}>
            Supported OpenAPI and Jinja tools, an official JavaScript runtime, and the final Rust language platform.
          </div>
          <div style={{ display: "flex", marginTop: "42px", gap: "14px", fontSize: "18px", color: "#f0c58e" }}>
            <span>codepot-openapi</span>
            <span style={{ color: "#9d826d" }}>→</span>
            <span>codepotg</span>
            <span style={{ color: "#9d826d" }}>→</span>
            <span>codepotx</span>
            <span style={{ color: "#9d826d" }}>→</span>
            <span>codepot</span>
          </div>
        </div>

        <div style={{ display: "flex", width: "36%", alignItems: "center", justifyContent: "center", zIndex: 2 }}>
          <div style={{ display: "flex", position: "relative", width: "330px", height: "420px", transform: "rotate(-10deg)" }}>
            <div
              style={{
                position: "absolute",
                width: "84px",
                height: "190px",
                left: "128px",
                top: "-42px",
                borderRadius: "50%",
                borderLeft: "18px solid rgba(238,204,160,.48)",
                transform: "rotate(18deg)",
              }}
            />
            <div
              style={{
                position: "absolute",
                width: "260px",
                height: "278px",
                left: "36px",
                bottom: "22px",
                borderRadius: "46%",
                background: "linear-gradient(145deg, #e2a663, #ae6233 50%, #63341e)",
                border: "8px solid #4f2918",
                boxShadow: "0 34px 48px rgba(0,0,0,.36)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "54px",
                fontWeight: 800,
                color: "#25130c",
              }}
            >
              {"</>"}
            </div>
            <div
              style={{
                position: "absolute",
                width: "250px",
                height: "76px",
                left: "41px",
                top: "102px",
                borderRadius: "50%",
                background: "linear-gradient(180deg, #f0c58e, #9b512b)",
                border: "8px solid #4f2918",
              }}
            />
            <div
              style={{
                position: "absolute",
                width: "150px",
                height: "38px",
                left: "91px",
                top: "121px",
                borderRadius: "50%",
                background: "#170c08",
              }}
            />
          </div>
        </div>
      </div>
    ),
    size,
  );
}
