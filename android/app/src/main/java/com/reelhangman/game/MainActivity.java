package com.reelhangman.game;

import android.graphics.Color;
import android.os.Bundle;
import android.view.ViewGroup;
import android.webkit.WebView;
import android.widget.FrameLayout;
import android.widget.ImageView;
import com.getcapacitor.BridgeActivity;
import com.getcapacitor.WebViewListener;

public class MainActivity extends BridgeActivity {

    private FrameLayout splashOverlay;
    private boolean splashDismissed;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        if (bridge != null && bridge.getWebView() != null) {
            bridge.getWebView().setBackgroundColor(Color.TRANSPARENT);
        }

        showSplashOverlay();

        if (bridge != null) {
            bridge.addWebViewListener(
                new WebViewListener() {
                    @Override
                    public void onPageCommitVisible(WebView view, String url) {
                        dismissSplashOverlay();
                    }

                    @Override
                    public void onPageLoaded(WebView webView) {
                        // onPageCommitVisible is the reliable signal. This
                        // fallback covers older WebView implementations.
                        if (splashOverlay != null) {
                            splashOverlay.postDelayed(MainActivity.this::dismissSplashOverlay, 450);
                        }
                    }
                }
            );
        }
    }

    private void showSplashOverlay() {
        ViewGroup root = findViewById(android.R.id.content);
        if (root == null) return;

        splashOverlay = new FrameLayout(this);
        splashOverlay.setBackgroundColor(Color.rgb(8, 9, 15));
        splashOverlay.setClickable(true);

        ImageView image = new ImageView(this);
        image.setImageResource(R.drawable.splash);
        image.setScaleType(ImageView.ScaleType.CENTER_CROP);
        splashOverlay.addView(
            image,
            new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        );

        root.addView(
            splashOverlay,
            new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        );

        // Never trap the player behind a splash if a WebView callback is lost.
        splashOverlay.postDelayed(this::dismissSplashOverlay, 7000);
    }

    private void dismissSplashOverlay() {
        if (splashDismissed || splashOverlay == null) return;
        splashDismissed = true;
        splashOverlay
            .animate()
            .alpha(0f)
            .setDuration(260)
            .withEndAction(() -> {
                ViewGroup parent = (ViewGroup) splashOverlay.getParent();
                if (parent != null) parent.removeView(splashOverlay);
                splashOverlay = null;
            })
            .start();
    }
}
