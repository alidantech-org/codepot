import { ImageResponse } from "next/og";

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "180px",
          height: "180px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
          overflow: "hidden",
          borderRadius: "38px",
          background: "linear-gradient(145deg, #2b190f, #4c2a18)",
        }}
      >
        <div
          style={{
            position: "absolute",
            width: "54px",
            height: "82px",
            left: "66px",
            top: "5px",
            borderRadius: "50%",
            borderLeft: "10px solid rgba(232,211,181,.72)",
            transform: "rotate(22deg)",
          }}
        />
        <div
          style={{
            width: "116px",
            height: "112px",
            marginTop: "34px",
            borderRadius: "46%",
            background: "linear-gradient(145deg, #e2a663, #a85e2e 52%, #673b24)",
            border: "5px solid #5c321d",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#25130c",
            fontSize: "30px",
            fontWeight: 800,
            transform: "rotate(-10deg)",
            boxShadow: "0 18px 28px rgba(0,0,0,.32)",
          }}
        >
          {"</>"}
        </div>
      </div>
    ),
    size,
  );
}
